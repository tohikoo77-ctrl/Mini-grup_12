from rest_framework import serializers

from product.models import Product

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    total_price = serializers.DecimalField(
        source="line_total",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "price_snapshot",
            "total_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "product",
            "product_name",
            "product_price",
            "price_snapshot",
            "total_price",
            "created_at",
            "updated_at",
        )


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source="get_items_count", read_only=True)
    total_quantity = serializers.IntegerField(
        source="get_total_quantity",
        read_only=True,
    )
    subtotal = serializers.DecimalField(
        source="get_subtotal",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    total_price = serializers.DecimalField(
        source="get_total_price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "is_active",
            "items",
            "items_count",
            "total_quantity",
            "subtotal",
            "total_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "items",
            "items_count",
            "total_quantity",
            "subtotal",
            "total_price",
            "created_at",
            "updated_at",
        )


class ProductIDSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()


class AddCartItemSerializer(ProductIDSerializer):
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        product = Product.objects.filter(
            id=attrs["product_id"],
            is_active=True,
            is_available=True,
        ).first()

        if product is None:
            raise serializers.ValidationError(
                {"product_id": ["mahsulot topilmadi yoki sotuvda mavjud emas."]}
            )

        attrs["product"] = product
        return attrs


class UpdateCartItemSerializer(ProductIDSerializer):
    quantity = serializers.IntegerField(min_value=1)


class RemoveCartItemSerializer(ProductIDSerializer):
    pass
