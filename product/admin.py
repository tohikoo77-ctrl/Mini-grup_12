from django.contrib import admin
from .models import Product, ProductImage, Favourite


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("image", "is_main", "created_at")
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

    list_filter = (
        "is_available",
        "is_active",
        "category",
        "seller",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "category__name",
        "seller__username",
        "seller__email",
    )

    ordering = ("-created_at",)

    prepopulated_fields = {"slug": ("name",)}

    list_select_related = ("category", "seller")

    inlines = (ProductImageInline,)

    readonly_fields = (
        "discount_price",
        "views",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "slug", "description")
        }),
        ("Pricing", {
            "fields": ("price", "old_price", "discount_price")
        }),
        ("Relations", {
            "fields": ("category", "seller")
        }),
        ("Status", {
            "fields": ("is_available", "is_active")
        }),
        ("Stats", {
            "fields": ("rating", "views")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    save_on_top = True
    list_per_page = 25


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "is_main",
        "created_at",
    )

    list_filter = (
        "is_main",
        "created_at",
    )

    search_fields = (
        "product__name",
    )

    list_select_related = ("product",)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "created_at",
    )

    list_filter = (
        "created_at",
        "user",
        "product",
    )

    search_fields = (
        "user__username",
        "product__name",
    )

    list_select_related = (
        "user",
        "product",
    )

    readonly_fields = ("created_at",)
    