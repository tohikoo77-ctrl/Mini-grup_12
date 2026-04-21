from django.contrib import admin
from .models import Category, CategoryProperty, PropertyOption


class PropertyOptionInline(admin.TabularInline):
    model = PropertyOption
    extra = 0


class CategoryPropertyInline(admin.TabularInline):
    model = CategoryProperty
    extra = 0


@admin.register(CategoryProperty)
class CategoryPropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "field_type", "is_required", "order")
    list_filter = ("field_type", "is_required")
    search_fields = ("name", "category__name")
    ordering = ("order",)
    inlines = (PropertyOptionInline,)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    ordering = ("order", "-created_at")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (CategoryPropertyInline,)


@admin.register(PropertyOption)
class PropertyOptionAdmin(admin.ModelAdmin):
    list_display = ("property", "value")
    search_fields = ("value", "property__name")
