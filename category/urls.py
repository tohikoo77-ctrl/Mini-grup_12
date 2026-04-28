from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CategoryPropertyViewSet, PropertyOptionViewSet

# Routerni sozlaymiz
router = DefaultRouter()

# Har bir viewset uchun aniq prefikslar (Postmandagi URLlar shunga qarab bo'ladi)
router.register("list", CategoryViewSet, basename="category")
router.register("property", CategoryPropertyViewSet, basename="category-property")
router.register("option", PropertyOptionViewSet, basename="category-option")

urlpatterns = [
    # Barcha router yo'llarini bittada ulaymiz
    path("", include(router.urls)),
]
