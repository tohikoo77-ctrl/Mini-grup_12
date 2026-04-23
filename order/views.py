from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderItem, PromoCode
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    AddItemSerializer,
    PromoApplySerializer,
)
from product.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        return Response({"error": "Use checkout instead"}, status=400)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        order = Order.objects.create(
            user=request.user,
            phone=request.data.get("phone"),
            shipping_address_snapshot=request.data.get("address"),
        )

        order.update_total_price()

        return Response(
            {
                "message": "Order created",
                "order_id": order.id,
                "total_price": order.total_price,
            }
        )

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        order = self.get_object()

        serializer = AddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(Product, id=serializer.validated_data["product_id"])

        quantity = serializer.validated_data["quantity"]

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_snapshot=product.price,
        )

        order.update_total_price()

        return Response({"message": "Item added", "total_price": order.total_price})

    @action(detail=True, methods=["post"])
    def apply_promocode(self, request, pk=None):
        order = self.get_object()

        serializer = PromoApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        promo = get_object_or_404(PromoCode, code=serializer.validated_data["code"])

        if not promo.is_valid():
            return Response({"error": "Promo invalid or expired"}, status=400)

        order.promocode = promo
        order.save()
        order.update_total_price()

        return Response(
            {
                "message": "Promo applied",
                "discount_percent": promo.discount_percent,
                "total_price": order.total_price,
            }
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status in ["shipped", "delivered"]:
            return Response(
                {"error": "Cannot cancel shipped/delivered order"}, status=400
            )

        order.status = "cancelled"
        order.save()

        return Response({"message": "Order cancelled"})

    @action(detail=False, methods=["get"])
    def my_orders(self, request):
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
