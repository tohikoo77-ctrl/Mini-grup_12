from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from order.models import Order, OrderItem
from order.serializers import CartCheckoutSerializer, OrderSerializer

from .models import Cart, CartItem
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    RemoveCartItemSerializer,
    UpdateCartItemSerializer,
)


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_serializer_class(self):
        if self.action == 'add_item':
            return AddCartItemSerializer
        if self.action == 'remove_item':
            return RemoveCartItemSerializer
        if self.action == 'update_item':
            return UpdateCartItemSerializer
        if self.action == 'checkout':
            return CartCheckoutSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return (
            Cart.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("items__product")
        )

    def get_cart(self, lock=False):
        queryset = Cart.objects
        if lock:
            queryset = queryset.select_for_update()

        cart, _ = queryset.get_or_create(user=self.request.user)
        return cart

    def serialize_cart(self, cart):
        cart = self.get_queryset().get(pk=cart.pk)
        return self.get_serializer(cart).data

    def cart_response(self, message, cart, response_status=status.HTTP_200_OK):
        return Response(
            {
                "message": message,
                "cart": self.serialize_cart(cart),
            },
            status=response_status,
        )

    def get_cart_item(self, cart, product_id):
        item = (
            CartItem.objects.select_related("product")
            .filter(cart=cart, product_id=product_id)
            .first()
        )

        if item is None:
            raise NotFound({"product_id": ["bu mahsulot savatda yo'q."]})

        return item

    @action(detail=False, methods=["get"])
    def my_cart(self, request):
        cart = self.get_cart()
        return Response(self.serialize_cart(cart))

    @action(detail=False, methods=["post"])
    def add_item(self, request):
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
    def remove_item(self, request):
        serializer = RemoveCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]

        with transaction.atomic():
            cart = get_object_or_404(Cart.objects.select_for_update(), user=request.user)
            item = self.get_cart_item(cart, product_id)
            item.delete()

        return self.cart_response("removed", cart)

    @action(detail=False, methods=["patch"])
    def update_item(self, request):
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
    def clear(self, request):
        with transaction.atomic():
            cart = self.get_cart(lock=True)
            cart.items.all().delete()

        return self.cart_response("cleared", cart)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        serializer = CartCheckoutSerializer(data=request.data)
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
                phone=serializer.validated_data["phone"],
                shipping_address_snapshot=serializer.validated_data[
                    "shipping_address_snapshot"
                ],
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
