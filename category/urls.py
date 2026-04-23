from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CategoryPropertyViewSet, PropertyOptionViewSet


router = DefaultRouter()
router.register("category", CategoryViewSet)
router.register("property", CategoryPropertyViewSet)
router.register("option", PropertyOptionViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
