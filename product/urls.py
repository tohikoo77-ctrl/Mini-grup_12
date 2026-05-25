from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FavouriteViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"favourites", FavouriteViewSet, basename="favourite")

urlpatterns = [
    # GET  /api/product/api/v1/products/         — ro'yxat + qidiruv
    # GET  /api/product/api/v1/products/<uuid>/  — ID bo'yicha bitta mahsulot
    path("api/v1/", include(router.urls)),
]
