from django.contrib import admin
from .models import Category, CategoryProperty, PropertyOption


class PropertyOptionInline(admin.TabularInline):
    model = PropertyOption
    extra = 0
    autocomplete_fields = ("property",)
    show_change_link = True
    classes = ("collapse",)


class CategoryPropertyInline(admin.TabularInline):
    model = CategoryProperty
    extra = 0
    autocomplete_fields = ("category",)
    show_change_link = True
    classes = ("collapse",)


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

    list_display_links = ("name",)

    list_filter = (
        "is_active",
        "is_deleted",
        "created_at",
        "parent",
    )

    search_fields = (
        "name",
        "slug",
        "parent__name",
    )

    ordering = ("order", "-created_at")

    prepopulated_fields = {"slug": ("name",)}

    autocomplete_fields = ("parent",)

    list_select_related = ("parent",)

    inlines = (CategoryPropertyInline,)

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "slug", "parent", "image", "icon")
        }),
        ("Business Status", {
            "fields": ("is_active", "is_deleted", "order")
        }),
        ("System Info", {
            "fields": ("created_at", "updated_at")
        }),
    )

    readonly_fields = ("created_at", "updated_at")

    save_on_top = True
    list_per_page = 25
    list_editable = ("order", "is_active")

    actions = ("make_active", "make_inactive")

    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(CategoryProperty)
class CategoryPropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "field_type",
        "is_required",
        "order",
    )

    list_display_links = ("name",)

    list_filter = (
        "category",
        "field_type",
        "is_required",
    )

    search_fields = (
        "name",
        "category__name",
    )

    autocomplete_fields = ("category",)

    ordering = ("category", "order")

    list_select_related = ("category",)

    inlines = (PropertyOptionInline,)

    fieldsets = (
        ("Property Info", {
            "fields": ("category", "name", "field_type")
        }),
        ("Rules", {
            "fields": ("is_required", "order")
        }),
    )

    save_on_top = True
    list_per_page = 50

    actions = ("make_required", "make_optional")

    def make_required(self, request, queryset):
        queryset.update(is_required=True)

    def make_optional(self, request, queryset):
        queryset.update(is_required=False)


@admin.register(PropertyOption)
class PropertyOptionAdmin(admin.ModelAdmin):
    list_display = (
        "value",
        "property",
        "get_category",
    )

    list_display_links = ("value",)

    list_filter = ("property__category",)

    search_fields = (
        "value",
        "property__name",
        "property__category__name",
    )

    autocomplete_fields = ("property",)

    list_select_related = ("property", "property__category")

    def get_category(self, obj):
        return obj.property.category

    get_category.short_description = "Category"
    get_category.admin_order_field = "property__category__name"
    