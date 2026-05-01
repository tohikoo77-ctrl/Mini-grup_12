from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, FavouriteViewSet

router = DefaultRouter()

router.register(r"products", ProductViewSet, basename="product")
router.register(r"favourites", FavouriteViewSet, basename="favourite")

urlpatterns = [
    path("api/v1/", include((router.urls, "shop"), namespace="v1")),
]
