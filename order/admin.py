from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("price_snapshot", "total_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_price",
        "phone",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("user__phone_number", "phone", "id")
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")

    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "quantity",
        "price_snapshot",
        "total_price",
    )

    search_fields = ("product__title", "order__id")
    list_filter = ("created_at",)

    ordering = ("-created_at",)
