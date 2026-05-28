import uuid

from django.db.models import Prefetch
from rest_framework import viewsets

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


def parse_uuid_list(uuid_string):
    if not uuid_string:
        return []

    valid_uuids = []
    for item in uuid_string.split(","):
        try:
            valid_uuids.append(uuid.UUID(item.strip()))
        except ValueError:
            continue
    return valid_uuids


class CategoryViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = Category.objects.select_related("parent").prefetch_related(
            "children",
            Prefetch(
                "properties",
                queryset=CategoryProperty.objects.prefetch_related("options"),
            ),
        )

        uuid_list = parse_uuid_list(self.request.query_params.get("in_pk"))
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)

        return CategoryFilter(qs, self.request.query_params).filter()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return CategoryListSerializer


class CategoryPropertyViewSet(viewsets.ModelViewSet):
    queryset = CategoryProperty.objects.select_related("category").prefetch_related(
        "options"
    )

    def get_queryset(self):
        qs = super().get_queryset()
        uuid_list = parse_uuid_list(self.request.query_params.get("in_pk"))
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CategoryPropertyCreateSerializer
        return CategoryPropertySerializer


class PropertyOptionViewSet(viewsets.ModelViewSet):
    queryset = PropertyOption.objects.select_related("property", "property__category")

    def get_queryset(self):
        qs = super().get_queryset()
        uuid_list = parse_uuid_list(self.request.query_params.get("in_pk"))
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PropertyOptionCreateSerializer
        return PropertyOptionSerializer
