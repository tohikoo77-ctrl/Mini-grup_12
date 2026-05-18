from django.contrib import admin
from .models import Order, OrderItem, PromoCode


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("price_snapshot", "total_price")
    can_delete = False


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

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "user__id",
        "user__phone_number",
        "phone",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "total_price",
        "created_at",
        "updated_at",
    )

    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "quantity",
        "price_snapshot",
        "total_price",
        "created_at",
    )

    search_fields = (
        "order__id",
        "product__name",
    )

    list_filter = ("created_at",)

    readonly_fields = (
        "total_price",
        "created_at",
    )


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_percent",
        "active",
        "valid_from",
        "valid_to",
        "is_valid_display",
        "created_at",
    )

    list_filter = (
        "active",
        "valid_from",
        "valid_to",
    )

    search_fields = ("code",)

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)

    def is_valid_display(self, obj):
        return obj.is_valid()

    is_valid_display.boolean = True
    is_valid_display.short_description = "Valid"
