from rest_framework import viewsets
from django.db.models import Prefetch

from .models import Category, CategoryProperty, PropertyOption
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryPropertySerializer,
    CategoryPropertyCreateSerializer,
    PropertyOptionSerializer,
    PropertyOptionCreateSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = (
        Category.active
        .select_related("parent")
        .prefetch_related(
            "children",
            Prefetch(
                "properties",
                queryset=CategoryProperty.objects.prefetch_related("options")
            ),
        )
    )

from .serializers import CategoryDetailSerializer, CategoryTreeSerializer
from .services import CategoryService


class CategoryViewSet(ReadOnlyModelViewSet):
    http_method_names = ["get"]

    def get_serializer_class(self):
        # Agar so'rov turi yaratish yoki o'zgartirish bo'lsa
        if self.action in ["create", "update", "partial_update"]:
            return CategoryPropertyCreateSerializer
        # Ro'yxatni ko'rish (GET) uchun eski serializer qoladi
        return CategoryPropertySerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return CategoryTreeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().filter(parent__isnull=True)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def get_serializer_class(self):

        if self.action in ["create", "update", "partial_update"]:
            return PropertyOptionCreateSerializer
        return PropertyOptionSerializer
    