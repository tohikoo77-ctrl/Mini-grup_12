from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Region, District, UserAddress
from .serializers import (
    RegionSerializer,
    DistrictSerializer,
    UserAddressSerializer,
    UserAddressCreateSerializer,
)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        region = self.request.query_params.get("region")
        if region:
            return District.objects.filter(region_id=region)
        return District.objects.all()


class UserAddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return UserAddressCreateSerializer
        return UserAddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
