from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("created_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
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
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "category__title",
        "seller__username",
    )

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
        "product__category__title",
    )

    readonly_fields = ("created_at",)
