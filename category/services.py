from django.db.models import Prefetch
from django.core.cache import cache

from .models import Category, CategoryProperty, PropertyOption


class CategoryService:
    CACHE_KEY = "category_queryset_v1"

    @staticmethod
    def queryset():
        cached = cache.get(CategoryService.CACHE_KEY)
        if cached:
            return cached

        base_qs = Category.objects.filter(is_deleted=False)

        children_qs = (
            Category.objects
            .filter(is_deleted=False)
            .select_related("parent")
            .order_by("order")
        )

        properties_qs = (
            CategoryProperty.objects
            .select_related("category")
            .prefetch_related(
                Prefetch(
                    "options",
                    queryset=PropertyOption.objects.only("id", "value").order_by("id"),
                )
            )
            .only("id", "name", "field_type", "is_required", "order", "category_id")
            .order_by("order")
        )

        qs = (
            base_qs
            .select_related("parent")
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=children_qs,
                    to_attr="_children_cache",
                ),
                Prefetch(
                    "properties",
                    queryset=properties_qs,
                    to_attr="_properties_cache",
                ),
            )
            .only(
                "id", "name", "slug", "parent_id",
                "image", "icon", "is_active",
                "is_deleted", "order"
            )
            .order_by("order")
        )

        cache.set(CategoryService.CACHE_KEY, qs, 60 * 10)  # 10 min cache
        return qs

    @staticmethod
    def invalidate_cache():
        cache.delete(CategoryService.CACHE_KEY)
        