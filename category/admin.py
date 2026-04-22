from django.contrib import admin
from .models import Category, CategoryProperty, PropertyOption


class PropertyOptionInline(admin.TabularInline):
    model = PropertyOption
    extra = 0
    show_change_link = True


class CategoryPropertyInline(admin.TabularInline):
    model = CategoryProperty
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "parent",
        "is_active",
        "order",
        "created_at",
    )

    list_filter = (
        "is_active",
        "parent",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
    )

    ordering = (
        "order",
        "-created_at",
    )

    prepopulated_fields = {"slug": ("name",)}

    inlines = (CategoryPropertyInline,)

    fieldsets = (
        ("Category Info", {
            "fields": ("name", "slug", "parent", "image", "icon")
        }),
        ("Settings", {
            "fields": ("is_active", "order")
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at")
        }),
    )

    readonly_fields = ("created_at", "updated_at")


@admin.register(CategoryProperty)
class CategoryPropertyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "field_type",
        "is_required",
        "order",
    )

    list_filter = (
        "category",
        "field_type",
        "is_required",
    )

    search_fields = (
        "name",
        "category__name",
    )

    ordering = (
        "category",
        "order",
    )

    inlines = (PropertyOptionInline,)


@admin.register(PropertyOption)
class PropertyOptionAdmin(admin.ModelAdmin):

    list_display = (
        "property",
        "value",
    )

    list_filter = (
        "property__category",
    )

    search_fields = (
        "value",
        "property__name",
        "property__category__name",
    )
    