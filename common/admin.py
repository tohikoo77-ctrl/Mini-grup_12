from django.contrib import admin
from .models import Region, District, UserAddress


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0
    show_change_link = True


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    ordering = ("order", "name")
    inlines = (DistrictInline,)
    readonly_fields = ("created_at",)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "order", "created_at")
    search_fields = ("name", "region__name")
    list_filter = ("region",)
    ordering = ("region", "order", "name")
    readonly_fields = ("created_at",)


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "region",
        "district",
        "address_line",
        "is_default",
        "created_at",
    )
    search_fields = (
        "user__phone_number",
        "region__name",
        "district__name",
        "address_line",
    )
    list_filter = ("region", "district", "is_default")
    ordering = ("-created_at",)

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Location", {"fields": ("region", "district", "address_line")}),
        ("Settings", {"fields": ("is_default",)}),
        ("Meta", {"fields": ("created_at",)}),
    )

    readonly_fields = ("created_at",)
