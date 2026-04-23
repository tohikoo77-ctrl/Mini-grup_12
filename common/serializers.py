from rest_framework import serializers
from .models import Region, District, UserAddress


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = "__all__"
        read_only_fields = ("user",)


class UserAddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ("region", "district", "address_line", "is_default")

    def create(self, validated_data):
        return UserAddress.objects.create(
            user=self.context["request"].user, **validated_data
        )
