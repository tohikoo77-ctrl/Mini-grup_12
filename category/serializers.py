from rest_framework import serializers
from .models import Category, CategoryProperty, PropertyOption


class PropertyOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOption
        fields = (
            "id",
            "value",
        )


class CategoryPropertySerializer(serializers.ModelSerializer):
    options = PropertyOptionSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryProperty
        fields = (
            "id",
            "name",
            "field_type",
            "is_required",
            "order",
            "options",
        )


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent",
            "is_active",
            "order",
        )


class CategoryDetailSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    properties = CategoryPropertySerializer(many=True, read_only=True)
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent",
            "image",
            "icon",
            "is_active",
            "is_deleted",
            "order",
            "full_path",
            "children",
            "properties",
        )

    def get_children(self, obj):
        # SAFE: works with prefetch or normal queryset
        children = getattr(obj, "children_all", None) or obj.children.all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "is_active": c.is_active,
                "order": c.order,
            }
            for c in children
        ]

    def get_full_path(self, obj):
        names = []
        current = obj

        while current:
            names.append(current.name)
            current = current.parent

        return " > ".join(reversed(names))
    