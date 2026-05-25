from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.mixins import UUIDLookupMixin
from order.models import Order, OrderItem
from order.serializers import OrderCreateSerializer, OrderSerializer

from .filters import CartFilter
from .models import Cart, CartItem
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    RemoveCartItemSerializer,
    UpdateCartItemSerializer,
)


class CartViewSet(UUIDLookupMixin, viewsets.ModelViewSet):
    """
    Savatlar: ro'yxat va ID bo'yicha bitta obyekt.

    GET  /api/card/              — foydalanuvchi savatlari (?id=)
    GET  /api/card/<uuid>/       — bitta savat
    GET  /api/card/my/           — joriy foydalanuvchi savati
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    lookup_field = "pk"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self) -> QuerySet[Cart]:
        qs = (
            Cart.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("items__product")
        )
        return CartFilter(qs, self.request.query_params).filter()

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Autentifikatsiya qilingan foydalanuvchining savatlari."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """ID bo'yicha savat; topilmasa 404."""
        cart = self.get_object()
        return Response(self.serialize_cart(cart))

    def get_cart(self, lock: bool = False) -> Cart:
        queryset = Cart.objects
        if lock:
            queryset = queryset.select_for_update()

        cart, _ = queryset.get_or_create(user=self.request.user)
        return cart

    def serialize_cart(self, cart: Cart) -> dict:
        cart = self.get_queryset().get(pk=cart.pk)
        return self.get_serializer(cart).data

    def cart_response(
        self,
        message: str,
        cart: Cart,
        response_status: int = status.HTTP_200_OK,
    ) -> Response:
        return Response(
            {
                "message": message,
                "cart": self.serialize_cart(cart),
            },
            status=response_status,
        )

    def get_cart_item(self, cart: Cart, product_id: Any) -> CartItem:
        item = (
            CartItem.objects.select_related("product")
            .filter(cart=cart, product_id=product_id)
            .first()
        )

        if item is None:
            raise NotFound({"product_id": ["bu mahsulot savatda yo'q."]})

        return item

    @action(detail=False, methods=["get"])
    def my_cart(self, request: Request) -> Response:
        cart = self.get_cart()
        return Response(self.serialize_cart(cart))

    @action(detail=False, methods=["post"])
    def add_item(self, request: Request) -> Response:
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            cart = self.get_cart(lock=True)
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart,
                product=product,
                defaults={
                    "quantity": quantity,
                    "price_snapshot": product.price,
                },
            )

            if not created:
                item.quantity += quantity
                item.save(update_fields=["quantity", "total_price", "updated_at"])

        return self.cart_response("added", cart, status.HTTP_201_CREATED)

    @action(detail=False, methods=["delete"])
    def remove_item(self, request: Request) -> Response:
        serializer = RemoveCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]

        with transaction.atomic():
            cart = get_object_or_404(Cart.objects.select_for_update(), user=request.user)
            item = self.get_cart_item(cart, product_id)
            item.delete()

        return self.cart_response("removed", cart)

    @action(detail=False, methods=["patch"])
    def update_item(self, request: Request) -> Response:
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            cart = get_object_or_404(Cart.objects.select_for_update(), user=request.user)
            item = self.get_cart_item(cart, product_id)
            item.quantity = quantity
            item.save(update_fields=["quantity", "total_price", "updated_at"])

        return self.cart_response("updated", cart)

    @action(detail=False, methods=["delete"])
    def clear(self, request: Request) -> Response:
        with transaction.atomic():
            cart = self.get_cart(lock=True)
            cart.items.all().delete()

        return self.cart_response("cleared", cart)

    @action(detail=False, methods=["post"])
    def checkout(self, request: Request) -> Response:
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            cart = self.get_cart(lock=True)
            cart_items = list(
                cart.items.select_for_update().select_related("product")
            )

            if not cart_items:
                raise ValidationError({"cart": ["Savat bo'sh."]})

            order = Order.objects.create(
                user=request.user,
                **serializer.validated_data,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_snapshot=item.price_snapshot,
                    total_price=item.total_price,
                )

            order.update_total_price()
            cart.items.all().delete()

        order_data = OrderSerializer(order, context=self.get_serializer_context()).data
        return Response(
            {"message": "Order created from cart", "order": order_data},
            status=status.HTTP_201_CREATED,
        )
