from __future__ import annotations

from typing import Any

from django.db.models import F, QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.mixins import UUIDLookupMixin

from .filters import ProductFilter
from .models import Favourite, Product
from .serializers import (
    FavouriteCreateSerializer,
    FavouriteListSerializer,
    ProductSerializer,
)


class ProductViewSet(
    UUIDLookupMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Mahsulotlar ro'yxati, qidiruv va ID bo'yicha bitta obyekt.

    GET  /api/product/api/v1/products/           — ro'yxat (?search=, ?id=, ...)
    GET  /api/product/api/v1/products/<uuid>/    — bitta mahsulot
    """

    serializer_class = ProductSerializer
    lookup_field = "pk"

    def get_queryset(self) -> QuerySet[Product]:
        qs = Product.objects.select_related(
            "category",
            "seller",
        ).prefetch_related("images")

        return ProductFilter(qs, self.request.query_params).filter()

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """ID bo'yicha mahsulot; topilmasa 404."""
        instance = self.get_object()

        Product.objects.filter(pk=instance.pk).update(views=F("views") + 1)
        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FavouriteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "create":
            return FavouriteCreateSerializer
        return FavouriteListSerializer

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user).select_related(
            "product", "product__category", "product__seller"
        ).prefetch_related("product__images")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
