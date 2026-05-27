from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryPropertyViewSet,
    CategoryViewSet,
    PropertyOptionViewSet,
)

# Router obyektini yaratamiz
router = DefaultRouter()

# ViewSet-larni mos URL yo'llari bilan ro'yxatdan o'tkazamiz
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"properties", CategoryPropertyViewSet, basename="category-property")
router.register(r"options", PropertyOptionViewSet, basename="property-option")

# Umumiy URL pattern-lar
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
