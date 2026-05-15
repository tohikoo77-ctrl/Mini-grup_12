from django.contrib import admin

from .models import Favourite, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

    fields = (
        "image",
        "is_main",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "seller",
        "price",
        "old_price",
        "discount_price",
        "is_available",
        "is_active",
        "rating",
        "views",
        "created_at",
    )

    list_display_links = (
        "name",
    )

    list_filter = (
        "is_available",
        "is_active",
        "category",
        "seller",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "category__name",
        "seller__username",
        "seller__email",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "category",
        "seller",
    )

    readonly_fields = (
        "discount_price",
        "views",
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    autocomplete_fields = (
        "category",
        "seller",
    )

    inlines = (
        ProductImageInline,
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                ),
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "old_price",
                    "discount_price",
                ),
            },
        ),
        (
            "Relations",
            {
                "fields": (
                    "category",
                    "seller",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_available",
                    "is_active",
                ),
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "rating",
                    "views",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    save_on_top = True

    list_per_page = 25

    date_hierarchy = "created_at"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "is_main",
        "created_at",
    )

    list_display_links = (
        "product",
    )

    list_filter = (
        "is_main",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__slug",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "product",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "product",
    )

    list_per_page = 25

    date_hierarchy = "created_at"


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "created_at",
    )

    list_display_links = (
        "user",
    )

    list_filter = (
        "created_at",
        "user",
    )

    search_fields = (
        "user__username",
        "user__email",
        "product__name",
        "product__slug",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "user",
        "product",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    list_per_page = 25

    date_hierarchy = "created_at"
    