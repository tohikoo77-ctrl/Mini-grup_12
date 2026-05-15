from rest_framework import serializers
from .models import Product, ProductImage, Favourite


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "is_main")


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    seller_name = serializers.CharField(source="seller.username", read_only=True)

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
            "category_name",
            "seller",
            "seller_name",
            "rating",
            "views",
            "images",
            "created_at",
        )
        

class FavouriteListSerializer(serializers.ModelSerializer):
    """Foydalanuvchining sevimli mahsulotlari ro'yxati uchun"""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Favourite
        fields = ['id', 'product', 'created_at']


class FavouriteCreateSerializer(serializers.ModelSerializer):
    """Mahsulotni sevimlilarga qo'shish uchun"""
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True, is_available=True),
        source='product'
    )

    class Meta:
        model = Favourite
        fields = ['product_id']

    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs['product']
        
        # Albatta unique ekanligini tekshiramiz
        if Favourite.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Bu mahsulot allaqachon sevimlilarga qo'shilgan.")
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)