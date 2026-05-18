from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, DistrictViewSet, UserAddressViewSet


router = DefaultRouter()
router.register("region", RegionViewSet)
router.register("district", DistrictViewSet)
router.register("address", UserAddressViewSet, basename="address")


urlpatterns = [
    path("", include(router.urls)),
]
