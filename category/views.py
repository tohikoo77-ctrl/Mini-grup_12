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

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return CategoryDetailSerializer


class CategoryPropertyViewSet(viewsets.ModelViewSet):
    queryset = (
        CategoryProperty.objects
        .select_related("category")
        .prefetch_related("options")
    )

    def get_serializer_class(self):
        # Agar so'rov turi yaratish yoki o'zgartirish bo'lsa
        if self.action in ["create", "update", "partial_update"]:
            return CategoryPropertyCreateSerializer
        # Ro'yxatni ko'rish (GET) uchun eski serializer qoladi
        return CategoryPropertySerializer


class PropertyOptionViewSet(viewsets.ModelViewSet):
    queryset = (
        PropertyOption.objects
        .select_related("property", "property__category")
    )

    def get_serializer_class(self):

        if self.action in ["create", "update", "partial_update"]:
            return PropertyOptionCreateSerializer
        return PropertyOptionSerializer
    