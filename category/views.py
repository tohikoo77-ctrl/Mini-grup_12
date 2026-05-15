from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import CategoryDetailSerializer, CategoryTreeSerializer
from .services import CategoryService


class CategoryViewSet(ReadOnlyModelViewSet):
    http_method_names = ["get"]

    def get_queryset(self):
        return CategoryService.queryset()

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

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    