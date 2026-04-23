from django.shortcuts import get_object_or_404
from rest_framework import viewsets
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
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    @action(detail=False, methods=["get"])
    def my_products(self, request):
        products = Product.objects.filter(seller=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def view(self, request, pk=None):
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
        return Favourite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        product = get_object_or_404(Product, id=product_id)

        fav, created = Favourite.objects.get_or_create(
            user=request.user, product=product
        )

        if not created:
            fav.delete()
            return Response({"message": "removed from favourites"})

        return Response({"message": "added to favourites"})

    @action(detail=False, methods=["get"])
    def my_favourites(self, request):
        favs = self.get_queryset()
        serializer = self.get_serializer(favs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["delete"])
    def remove(self, request, pk=None):
        fav = self.get_object()
        fav.delete()
        return Response({"message": "deleted"})
