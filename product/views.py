from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Product, Favourite
from .serializers import (
    ProductSerializer,
    ProductCreateUpdateSerializer,
    FavouriteSerializer,
    FavouriteCreateSerializer,
)

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()

    def get_serializer_class(self):
        # Yaratish va yangilash uchun alohida serializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        # Mahsulot yaratuvchisini (seller) avtomatik aniqlash
        serializer.save(seller=self.request.user)

    @action(detail=False, methods=["get"])
    def my_products(self, request):
        """Foydalanuvchining o'zi qo'shgan mahsulotlar ro'yxati"""
        products = Product.objects.filter(seller=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def view(self, request, pk=None):
        """Mahsulot ko'rilganlar sonini oshirish"""
        product = self.get_object()
        product.views += 1
        product.save()
        return Response({"views": product.views})


class FavouriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Favourite.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return FavouriteCreateSerializer
        return FavouriteSerializer

    def get_queryset(self):
        # Faqat joriy foydalanuvchining saralanganlarini qaytarish
        return Favourite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Saralanganlarga qo'shish yoki o'chirish (Toggle mantiqi)
        Postman'da: {"product": "UUID_KODI"} yuboriladi
        """
        # Serializer'dan yoki to'g'ridan-to'g'ri datadan ID ni olamiz
        product_id = request.data.get("product") or request.data.get("product_id")
        
        if not product_id:
            return Response(
                {"error": "Product ID is required. Send 'product' field."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        product = get_object_or_404(Product, id=product_id)

        # get_or_create: bo'lsa oladi, bo'lmasa yaratadi
        fav, created = Favourite.objects.get_or_create(
            user=request.user, 
            product=product
        )

        if not created:
            # Agar allaqachon bor bo'lsa, o'chirib tashlaymiz (Toggle)
            fav.delete()
            return Response(
                {"message": "Removed from favourites", "is_favourite": False}, 
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "Added to favourites", "is_favourite": True}, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def my_favourites(self, request):
        """Mening barcha saralangan mahsulotlarim"""
        favs = self.get_queryset()
        serializer = self.get_serializer(favs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["delete"])
    def remove(self, request, pk=None):
        """Saralanganlardan aniq birini ID bo'yicha o'chirish"""
        fav = self.get_object()
        fav.delete()
        return Response({"message": "Deleted from favourites"}, status=status.HTTP_204_NO_CONTENT)
