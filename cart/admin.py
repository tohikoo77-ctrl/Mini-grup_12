from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("price_at_time",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "quantity", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__phone_number",)
    ordering = ("-created_at",)
    inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "cart",
        "quantity",
        "price_snapshot",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "product_name",
        "cart__user__phone_number",
    )
    ordering = ("-created_at",)
