from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from product.models import Product


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def my_cart(self, request):
        """Savatni ko'rish yoki yo'q bo'lsa yaratish"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Savatga mahsulot qo'shish"""
        cart, created = Cart.objects.get_or_create(user=request.user)

        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        product = get_object_or_404(Product, id=product_id)
        quantity = serializer.validated_data["quantity"]

        # get_or_create mahsulot savatda bor-yo'qligini tekshiradi
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity, "price_snapshot": product.price},
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response({
            "message": "added", 
            "total_price": cart.get_total_price()
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        """Savatdan mahsulotni o'chirish (DELETE metodi uchun)"""
        cart = get_object_or_404(Cart, user=request.user)
        product_id = request.data.get("product_id")

        # product__id orqali qidirish xatolikni oldini oladi
        item = get_object_or_404(CartItem, cart=cart, product__id=product_id)
        item.delete()

        return Response({
            "message": "removed", 
            "total_price": cart.get_total_price()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"])
    def update_item(self, request):
        """Mahsulot miqdorini o'zgartirish (PATCH metodi uchun)"""
        cart = get_object_or_404(Cart, user=request.user)

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        item = get_object_or_404(CartItem, cart=cart, product__id=product_id)
        item.quantity = quantity
        item.save()

        return Response({
            "message": "updated", 
            "total_price": cart.get_total_price()
        }, status=status.HTTP_200_OK)
