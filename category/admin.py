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
        "is_deleted",
        "order",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_deleted",
        "parent",
    )

    search_fields = (
        "name",
        "slug",
    )

    ordering = (
        "order",
        "-created_at",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_select_related = (
        "parent",
    )

    inlines = (
        CategoryPropertyInline,
    )

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "slug", "parent", "image", "icon")
        }),
        ("Status", {
            "fields": ("is_active", "is_deleted", "order")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    save_on_top = True
    list_per_page = 25
    list_editable = ("order", "is_active")


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

    list_select_related = (
        "category",
    )

    inlines = (
        PropertyOptionInline,
    )

    save_on_top = True
    list_per_page = 50


@admin.register(PropertyOption)
class PropertyOptionAdmin(admin.ModelAdmin):
    list_display = (
        "value",
        "property",
        "get_category",
    )

    list_filter = (
        "property__category",
    )

    search_fields = (
        "value",
        "property__name",
        "property__category__name",
    )

    list_select_related = (
        "property",
        "property__category",
    )

    def get_category(self, obj):
        return obj.property.category

    get_category.short_description = "Category"
    get_category.admin_order_field = "property__category"
    