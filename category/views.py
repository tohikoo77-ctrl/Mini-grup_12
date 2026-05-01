from rest_framework import viewsets
from django.db.models import Prefetch

from .models import Category, CategoryProperty, PropertyOption
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryPropertySerializer,
    PropertyOptionSerializer,
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

    serializer_class = CategoryPropertySerializer


class PropertyOptionViewSet(viewsets.ModelViewSet):
    queryset = (
        PropertyOption.objects
        .select_related("property", "property__category")
    )

    serializer_class = PropertyOptionSerializer
    