from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CategoryPropertyViewSet,
    PropertyOptionViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"properties", CategoryPropertyViewSet, basename="category-property")
router.register(r"options", PropertyOptionViewSet, basename="property-option")


urlpatterns = [
    path("api/v1/category/", include(router.urls)),
]
