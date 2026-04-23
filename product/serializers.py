from rest_framework import serializers
from .models import Product, ProductImage, Favourite


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "is_main", "created_at")


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "price",
            "old_price",
            "discount_price",
            "is_available",
            "is_active",
            "category",
            "seller",
            "rating",
            "views",
            "created_at",
            "updated_at",
            "images",
        )
        read_only_fields = ("slug", "discount_price", "rating", "views")


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "old_price",
            "category",
        )


class FavouriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Favourite
        fields = ("id", "product", "created_at")


class FavouriteCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
