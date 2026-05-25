from __future__ import annotations

from typing import Any, Type

from django.db.models import Prefetch, QuerySet
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from common.mixins import UUIDLookupMixin

from .filters import CategoryFilter
from .models import Category, CategoryProperty, PropertyOption
from .serializers import (
    CategoryDetailSerializer,
    CategoryListSerializer,
    CategoryPropertyCreateSerializer,
    CategoryPropertySerializer,
    PropertyOptionCreateSerializer,
    PropertyOptionSerializer,
)


class CategoryViewSet(UUIDLookupMixin, viewsets.ModelViewSet):
    """
    Kategoriyalar: ro'yxat, qidiruv va ID bo'yicha bitta obyekt.

    GET  /api/category/api/v1/categories/           — ro'yxat (?search=, ?id=)
    GET  /api/category/api/v1/categories/<uuid>/    — bitta kategoriya
    """

    lookup_field = "pk"

    def get_queryset(self) -> QuerySet[Category]:
        qs = (
            Category.active.select_related("parent").prefetch_related(
                "children",
                Prefetch(
                    "properties",
                    queryset=CategoryProperty.objects.prefetch_related("options"),
                ),
            )
        )
        return CategoryFilter(qs, self.request.query_params).filter()

    def get_serializer_class(self) -> Type[Any]:
        if self.action == "list":
            return CategoryListSerializer
        return CategoryDetailSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """ID bo'yicha kategoriya; topilmasa 404."""
        return super().retrieve(request, *args, **kwargs)


class CategoryPropertyViewSet(viewsets.ModelViewSet):
    queryset = (
        CategoryProperty.objects.select_related("category").prefetch_related(
            "options"
        )
    )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CategoryPropertyCreateSerializer
        return CategoryPropertySerializer


class PropertyOptionViewSet(viewsets.ModelViewSet):
    queryset = PropertyOption.objects.select_related(
        "property", "property__category"
    )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PropertyOptionCreateSerializer
        return PropertyOptionSerializer
