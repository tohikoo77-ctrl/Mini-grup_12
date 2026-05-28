from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryPropertyViewSet,
    CategoryViewSet,
    PropertyOptionViewSet,
)

# Router obyektini yaratamiz
router = DefaultRouter()

<<<<<<< HEAD
=======
# ViewSet-larni mos URL yo'llari bilan ro'yxatdan o'tkazamiz
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"properties", CategoryPropertyViewSet, basename="category-property")
router.register(r"options", PropertyOptionViewSet, basename="property-option")

# Umumiy URL pattern-lar
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
