from django.contrib import admin
from .models import Product, ProductImage, Favourite


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "is_main", "created_at")
    readonly_fields = ("created_at",)


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
        "description",
        "category__name",
        "seller__username",
    )

    list_select_related = ("category", "seller")

    prepopulated_fields = {"slug": ("name",)}

    inlines = (ProductImageInline,)

    readonly_fields = (
        "discount_price",
        "rating",
        "views",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


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
        "product__category__name",
        "product__seller__username",
    )

    list_select_related = ("product",)

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "created_at",
    )

    list_filter = (
        "user",
        "created_at",
    )

    search_fields = (
        "user__username",
        "product__name",
        "product__category__name",
    )

    list_select_related = ("user", "product")

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)
