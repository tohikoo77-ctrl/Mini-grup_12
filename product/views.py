from django.shortcuts import get_object_or_404
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Product, Favourite
from .serializers import (
    ProductSerializer,
    ProductCreateUpdateSerializer,
    FavouriteSerializer,
    FavouriteCreateSerializer,
)


# =========================
# 🛍 PRODUCT VIEWSET
# =========================
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.select_related("category", "seller")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        products = Product.objects.filter(seller=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def increment_view(self, request, pk=None):
        Product.objects.filter(pk=pk).update(views=F("views") + 1)
        product = self.get_object()
        return Response({"views": product.views}, status=status.HTTP_200_OK)


# =========================
# ❤️ FAVOURITE VIEWSET
# =========================
class FavouriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Favourite.objects.select_related("user", "product")

    def get_serializer_class(self):
        if self.action == "create":
            return FavouriteCreateSerializer
        return FavouriteSerializer

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product")

        if not product_id:
            return Response(
                {"detail": "product field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(Product, pk=product_id)

        favourite = Favourite.objects.filter(user=request.user, product=product)

        if favourite.exists():
            favourite.delete()
            return Response(
                {"message": "Removed from favourites", "is_favourite": False},
                status=status.HTTP_200_OK,
            )

        Favourite.objects.create(user=request.user, product=product)

        return Response(
            {"message": "Added to favourites", "is_favourite": True},
            status=status.HTTP_201_CREATED,
        )
