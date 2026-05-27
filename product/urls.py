from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FavouriteViewSet, ProductViewSet

# Router obyektini yaratamiz va viewset-larni ro'yxatdan o'tkazamiz
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"favourites", FavouriteViewSet, basename="favourite")

# URL pattern-lar ro'yxati
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
