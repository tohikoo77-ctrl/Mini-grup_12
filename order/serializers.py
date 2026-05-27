from rest_framework import serializers

from product.models import Product

from .models import Order, OrderItem, PromoCode


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = (
            "code",
            "discount_percent",
            "active",
            "valid_from",
            "valid_to",
        )


class OrderItemSerializer(serializers.ModelSerializer):
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
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "price_snapshot",
            "total_price",
            "created_at",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    promocode_code = serializers.CharField(source="promocode.code", read_only=True)
    discount_percent = serializers.IntegerField(
        source="get_discount_percent",
        read_only=True,
    )
    discount_amount = serializers.DecimalField(
        source="get_discount_amount",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    subtotal = serializers.DecimalField(
        source="get_subtotal",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    items_count = serializers.IntegerField(source="get_items_count", read_only=True)
    total_quantity = serializers.IntegerField(
        source="get_total_quantity",
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "status",
            "phone",
            "shipping_address_snapshot",
            "promocode",
            "promocode_code",
            "items",
            "items_count",
            "total_quantity",
            "subtotal",
            "discount_percent",
            "discount_amount",
            "total_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "promocode",
            "promocode_code",
            "items",
            "items_count",
            "total_quantity",
            "subtotal",
            "discount_percent",
            "discount_amount",
            "total_price",
            "created_at",
            "updated_at",
        )


class OrderUpdateSerializer(serializers.ModelSerializer):
    address = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = ("phone", "shipping_address_snapshot", "address")
        extra_kwargs = {
            "shipping_address_snapshot": {"required": False},
        }

    def validate(self, attrs):
        address = attrs.pop("address", None)
        snapshot = attrs.get("shipping_address_snapshot") or address

        if not snapshot:
            raise serializers.ValidationError(
                {"shipping_address_snapshot": ["yetkazib berish manzili kerak."]}
            )

        attrs["shipping_address_snapshot"] = snapshot
        return attrs


# BU YERDA OZGARISH QILINDI: order_id -> checkout_id
class OrderCreateSerializer(serializers.Serializer):
    checkout_id = serializers.UUIDField()


class CartCheckoutSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    shipping_address_snapshot = serializers.JSONField(required=False)
    address = serializers.JSONField(required=False)

    def validate(self, attrs):
        snapshot = attrs.get("shipping_address_snapshot") or attrs.pop("address", None)
        if not snapshot:
            raise serializers.ValidationError(
                {"shipping_address_snapshot": ["yetkazib berish manzili kerak."]}
            )
        attrs["shipping_address_snapshot"] = snapshot
        return attrs


class ProductIDSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()


class AddItemSerializer(ProductIDSerializer):
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


class PromoApplySerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        value = value.strip()
        promo = PromoCode.objects.filter(code__iexact=value).first()

        if promo is None:
            raise serializers.ValidationError("promo code topilmadi.")

        if not promo.is_valid():
            raise serializers.ValidationError("promo code yaroqsiz yoki muddati o'tgan.")

        self.context["promo"] = promo
        return promo.code
