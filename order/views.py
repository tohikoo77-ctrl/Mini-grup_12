import uuid
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import OrderFilter
from .models import Order, OrderItem
from .serializers import (
    AddItemSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
    PromoApplySerializer,
)


def parse_uuid_list(uuid_string):
    """
    Vergul bilan ajratilgan UUID qatorini toza UUID obyektlari ro'yxatiga o'tkazadi.
    Noto'g'ri qiymatlarni o'tkazib yuboradi (baza xatolik bermasligi uchun).
    """
    if not uuid_string:
        return []
        
    valid_uuids = []
    for item in uuid_string.split(','):
        cleaned_item = item.strip()
        try:
            valid_uuids.append(uuid.UUID(cleaned_item))
        except ValueError:
            continue
            
    return valid_uuids


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 1. Birlamchi optimallashtirilgan query yaratamiz
        qs = (
            Order.objects.filter(user=self.request.user)
            .select_related("user", "promocode")
            .prefetch_related("items__product")
        )
        
        # 2. URL query parametridan ?inpk=uuid1,uuid2 ni olamiz
        inpk = self.request.query_params.get('inpk')
        uuid_list = parse_uuid_list(inpk)
        
        # 3. Agar to'g'ri UUID-lar bo'lsa, queryset-ni filtrlaymiz
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)
            
        return OrderFilter(qs, self.request.query_params).filter()

    def get_serializer_class(self):
        if self.action == "checkout":
            return OrderCreateSerializer
        if self.action in {"update", "partial_update"}:
            return OrderUpdateSerializer
        return OrderSerializer

    def serialize_order(self, order):
        # inpk parametri serialize_order ichidagi .get(pk=order.pk) ni buzmasligi uchun 
        # get_queryset() o'rniga Order modelidan to'g'ridan-to'g'ri chaqiramiz
        order = (
            Order.objects.select_related("user", "promocode")
            .prefetch_related("items__product")
            .get(pk=order.pk)
        )
        return OrderSerializer(order, context=self.get_serializer_context()).data

    def order_response(self, message, order, response_status=status.HTTP_200_OK):
        return Response(
            {
                "message": message,
                "order": self.serialize_order(order),
            },
            status=response_status,
        )

    def ensure_modifiable(self, order):
        if not order.can_be_modified():
            raise ValidationError(
                {"status": ["bu holatdagi orderni o'zgartirib bo'lmaydi."]}
            )

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "orders/create/ endpointidan foydalaning."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        order = self.get_object()
        self.ensure_modifiable(order)

        serializer = self.get_serializer(order, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        order.update_total_price()

        return self.order_response("Order updated", order)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()

        if not order.can_be_cancelled():
            raise ValidationError(
                {"status": ["bu holatdagi orderni o'chirib bo'lmaydi."]}
            )

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self.get_queryset().select_for_update().filter(
            pk=serializer.validated_data["checkout_id"]
        ).first()

        if order is None:
            raise ValidationError({"order_id": ["order topilmadi."]})

        self.ensure_modifiable(order)
        return self.order_response("Order created", order, status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        serializer = AddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=self.get_object().pk)
            self.ensure_modifiable(order)

            existing_items = list(
                OrderItem.objects.select_for_update()
                .filter(order=order, product=product)
                .order_by("created_at")
            )

            if existing_items:
                item = existing_items[0]
                item.quantity = sum(i.quantity for i in existing_items) + quantity
                item.save(
                    update_fields=["quantity", "total_price"],
                    update_order_total=False,
                )

                duplicate_ids = [i.pk for i in existing_items[1:]]
                if duplicate_ids:
                    OrderItem.objects.filter(pk__in=duplicate_ids).delete()
            else:
                item = OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_snapshot=product.price,
                )
                item.save(update_order_total=False)

            order.update_total_price()

        return self.order_response("Item added", order, status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def apply_promocode(self, request, pk=None):
        serializer = PromoApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promo = serializer.context["promo"]

        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=self.get_object().pk)
            self.ensure_modifiable(order)

            order.promocode = promo
            order.save(update_fields=["promocode", "updated_at"])
            order.update_total_price()

        return self.order_response("Promo applied", order)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if not order.can_be_cancelled():
            raise ValidationError(
                {"status": ["shipped, delivered yoki cancelled order bekor qilinmaydi."]}
            )

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])

        return self.order_response("Order cancelled", order)

    @action(detail=False, methods=["get"])
    def my_orders(self, request):
        orders = self.get_queryset()
        serializer = OrderSerializer(
            orders,
            many=True,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)
