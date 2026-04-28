from rest_framework import serializers
from .models import Category, CategoryProperty, PropertyOption


class PropertyOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOption
        fields = ["id", "property", "value"] # 'property' maydoni qo'shildi


class CategoryPropertySerializer(serializers.ModelSerializer):
    options = PropertyOptionSerializer(many=True, read_only=True)
    # Postmandan ID yuborganda qabul qilishi uchun:
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = CategoryProperty
        fields = ["id", "category", "name", "field_type", "is_required", "order", "options"]


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    properties = CategoryPropertySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "image",
            "icon",
            "is_active",
            "order",
            "children",
            "properties",
        ]

    def get_children(self, obj):
        # Rekursiv ravishda farzand kategoriyalarni olish
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []
