from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    # Mahsulot nomini ham ko'rish uchun (ixtiyoriy lekin foydali)
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "price_snapshot",
            "total_price",
            "created_at",
        )

    def get_total_price(self, obj):
        return obj.quantity * obj.price_snapshot


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "is_active",
            "items",
            "total_quantity",
            "total_price",
            "created_at",
        )
        read_only_fields = ("user",)

    def get_total_quantity(self, obj):
        return obj.get_total_quantity()

    def get_total_price(self, obj):
        return obj.get_total_price()


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    # MUHIM: Bu yerda product_id bo'lishi shart, aks holda views.py da xato beradi
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
