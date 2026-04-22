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
        "category__name",
    )

    prepopulated_fields = {"slug": ("name",)}

    inlines = (ProductImageInline,)

    readonly_fields = (
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

    list_filter = ("is_main",)

    search_fields = (
        "product__name",
        "product__category__name",
    )