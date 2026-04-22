from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("total_price", "created_at", "updated_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__phone_number",)
    ordering = ("-created_at",)
    inlines = (CartItemInline,)
    readonly_fields = ("created_at", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "price_snapshot",
        "total_price",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("product__name", "cart__user__phone_number")
    readonly_fields = ("total_price", "created_at", "updated_at")
    ordering = ("-created_at",)
