from rest_framework import serializers
from .models import Category


class PropertyOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOption
        fields = (
            "id",
            "value",
        )


class PropertyOptionCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PropertyOption
        fields = (
            "id",
            "property",
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


class CategoryPropertyCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryProperty
        fields = (
            "id",
            "category",      
            "name",
            "field_type",
            "is_required",
            "order",
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
    properties = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent",
            "parent_name",
            "image",
            "icon",
            "is_active",
            "order",
            "children",
            "properties",
            "full_path",
        )

    def get_children(self, obj):
        return [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "is_active": c.is_active,
                "order": c.order,
            }
            for c in (getattr(obj, "_children_cache", []) or [])
        ]

    def get_properties(self, obj):
        result = []

        for p in (getattr(obj, "_properties_cache", []) or []):
            result.append({
                "id": p.id,
                "name": p.name,
                "field_type": p.field_type,
                "is_required": p.is_required,
                "order": p.order,
                "options": [
                    {
                        "id": o.id,
                        "value": o.value,
                    }
                    for o in (getattr(p, "_options_cache", []) or p.options.all())
                ],
            })

        return result

    def get_full_path(self, obj):
        return obj.get_full_path()
    