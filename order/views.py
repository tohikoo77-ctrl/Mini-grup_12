from __future__ import annotations

from typing import Any, Type

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.mixins import UUIDLookupMixin

from .filters import OrderFilter
from .models import Order, OrderItem
from .serializers import (
    AddItemSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    PromoApplySerializer,
)


class OrderViewSet(UUIDLookupMixin, viewsets.ModelViewSet):
    """
    Buyurtmalar: ro'yxat, qidiruv va ID bo'yicha bitta obyekt.

    GET  /api/order/orders/              — ro'yxat (?search=, ?id=, ?status=)
    GET  /api/order/orders/<uuid>/       — bitta buyurtma
    """

    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self) -> QuerySet[Order]:
        qs = (
            Order.objects.filter(user=self.request.user)
            .select_related("user", "promocode")
            .prefetch_related("items__product")
        )
        return OrderFilter(qs, self.request.query_params).filter()

    def get_serializer_class(self) -> Type[Any]:
        if self.action in {"checkout", "create", "update", "partial_update"}:
            return OrderCreateSerializer
        return OrderSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Foydalanuvchi buyurtmalarini qidiruv/filtr bilan qaytaradi."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """ID bo'yicha buyurtma; topilmasa 404."""
        order = self.get_object()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def serialize_order(self, order: Order) -> dict:
        order = self.get_queryset().get(pk=order.pk)
        return OrderSerializer(order, context=self.get_serializer_context()).data

    def order_response(
        self,
        message: str,
        order: Order,
        response_status: int = status.HTTP_200_OK,
    ) -> Response:
        return Response(
            {
                "message": message,
                "order": self.serialize_order(order),
            },
            status=response_status,
        )

    def ensure_modifiable(self, order: Order) -> None:
        if not order.can_be_modified():
            raise ValidationError(
                {"status": ["bu holatdagi orderni o'zgartirib bo'lmaydi."]}
            )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response(
            {"detail": "orders/create/ endpointidan foydalaning."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        order = self.get_object()
        self.ensure_modifiable(order)

        serializer = self.get_serializer(order, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        order.update_total_price()

        return self.order_response("Order updated", order)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        order = self.get_object()

        if not order.can_be_cancelled():
            raise ValidationError(
                {"status": ["bu holatdagi orderni o'chirib bo'lmaydi."]}
            )

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def checkout(self, request: Request) -> Response:
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self.get_queryset().select_for_update().filter(
            pk=serializer.validated_data["order_id"]
        ).first()

        if order is None:
            raise ValidationError({"order_id": ["order topilmadi."]})

        self.ensure_modifiable(order)
        return self.order_response("Order created", order, status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def add_item(self, request: Request, pk: str | None = None) -> Response:
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
    def apply_promocode(self, request: Request, pk: str | None = None) -> Response:
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
    def cancel(self, request: Request, pk: str | None = None) -> Response:
        order = self.get_object()

        if not order.can_be_cancelled():
            raise ValidationError(
                {
                    "status": [
                        "shipped, delivered yoki cancelled order bekor qilinmaydi."
                    ]
                }
            )

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])

        return self.order_response("Order cancelled", order)

    @action(detail=False, methods=["get"])
    def my_orders(self, request: Request) -> Response:
        orders = self.filter_queryset(self.get_queryset())
        serializer = OrderSerializer(
            orders,
            many=True,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)
