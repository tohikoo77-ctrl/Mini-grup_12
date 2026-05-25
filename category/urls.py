from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryPropertyViewSet,
    CategoryViewSet,
    PropertyOptionViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"properties", CategoryPropertyViewSet, basename="category-property")
router.register(r"options", PropertyOptionViewSet, basename="property-option")

urlpatterns = [
    # GET  /api/category/api/v1/categories/         — ro'yxat + qidiruv
    # GET  /api/category/api/v1/categories/<uuid>/  — ID bo'yicha bitta kategoriya
    path("api/v1/", include(router.urls)),
]
