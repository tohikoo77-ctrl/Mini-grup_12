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

from .serializers import CategoryDetailSerializer, CategoryTreeSerializer
from .services import CategoryService


<<<<<<< HEAD
class CategoryViewSet(ReadOnlyModelViewSet):
    http_method_names = ["get"]
=======
class CategoryPropertyViewSet(viewsets.ModelViewSet):
    queryset = (
        CategoryProperty.objects.select_related("category").prefetch_related(
            "options"
        )
    )
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c

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

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return CategoryTreeSerializer

<<<<<<< HEAD
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().filter(parent__isnull=True)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
=======
class PropertyOptionViewSet(viewsets.ModelViewSet):
    queryset = PropertyOption.objects.select_related(
        "property", "property__category"
    )
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c

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
