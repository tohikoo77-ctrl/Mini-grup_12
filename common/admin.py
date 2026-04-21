from django.contrib import admin
from .models import Region, District

# Register your models here.


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "created_at")
    search_fields = ("name",)
    ordering = ("order", "name")
    inlines = (DistrictInline,)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "order")
    list_filter = ("region",)
    search_fields = ("name", "region__name")
    ordering = ("region", "order", "name")
