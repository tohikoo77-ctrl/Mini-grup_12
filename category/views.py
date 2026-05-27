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
    """
    Строку из UUID, разделенных запятыми, превращает в список валидных UUID.
    Игнорирует некорректные строки, защищая от ошибок базы данных.
    """
    if not uuid_string:
        return []
        
    valid_uuids = []
    for item in uuid_string.split(','):
        cleaned_item = item.strip()
        try:
            # Пытаемся преобразовать в объект UUID
            valid_uuids.append(uuid.UUID(cleaned_item))
        except ValueError:
            # Если строка - не валидный UUID, просто пропускаем её
            continue
            
    return valid_uuids


class CategoryViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = (
            Category.active.select_related("parent").prefetch_related(
                "children",
                Prefetch(
                    "properties",
                    queryset=CategoryProperty.objects.prefetch_related("options"),
                ),
            )
        )
        
        # Получаем UUID из query_params (например, ?in_pk=uuid1,uuid2)
        in_pk = self.request.query_params.get('in_pk')
        uuid_list = parse_uuid_list(in_pk)
        
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)

        return CategoryFilter(qs, self.request.query_params).filter()

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return CategoryDetailSerializer


class CategoryPropertyViewSet(viewsets.ModelViewSet):
    queryset = (
        CategoryProperty.objects.select_related("category").prefetch_related(
            "options"
        )
    )

    def get_queryset(self):
        qs = super().get_queryset()
        
        in_pk = self.request.query_params.get('in_pk')
        uuid_list = parse_uuid_list(in_pk)
        
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)
            
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CategoryPropertyCreateSerializer
        return CategoryPropertySerializer


class PropertyOptionViewSet(viewsets.ModelViewSet):
    queryset = PropertyOption.objects.select_related(
        "property", "property__category"
    )

    def get_queryset(self):
        qs = super().get_queryset()
        
        in_pk = self.request.query_params.get('in_pk')
        uuid_list = parse_uuid_list(in_pk)
        
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)
            
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PropertyOptionCreateSerializer
        return PropertyOptionSerializer
