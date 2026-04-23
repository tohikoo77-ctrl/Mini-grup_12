from rest_framework import viewsets
from .models import Category, CategoryProperty, PropertyOption
from .serializers import (
    CategorySerializer,
    CategoryPropertySerializer,
    PropertyOptionSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryPropertyViewSet(viewsets.ModelViewSet):
    queryset = CategoryProperty.objects.all()
    serializer_class = CategoryPropertySerializer


class PropertyOptionViewSet(viewsets.ModelViewSet):
    queryset = PropertyOption.objects.all()
    serializer_class = PropertyOptionSerializer
