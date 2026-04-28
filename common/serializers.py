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
    # Ko'rish (List/Retrieve) paytida viloyat va tuman nomlarini chiqarish uchun
    region_name = serializers.ReadOnlyField(source='region.name')
    district_name = serializers.ReadOnlyField(source='district.name')

    class Meta:
        model = UserAddress
        fields = (
            "id", "user", "region", "region_name", 
            "district", "district_name", "address_line", "is_default"
        )
        read_only_fields = ("user",)


class UserAddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        # 'is_main' o'rniga 'is_default' ishlatildi
        fields = ("region", "district", "address_line", "is_default")

    # DIQQAT: Bu yerda 'create' metodi olib tashlandi, 
    # chunki views.py dagi perform_create bu vazifani bajaradi.
