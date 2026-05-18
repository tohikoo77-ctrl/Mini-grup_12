from django.contrib import admin
from .models import News

# Register your models here.


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "views",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published", "category", "created_at")
    search_fields = (
        "title",
        "content",
        "slug",
        "category__name",
        "author__phone_number",
    )
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views", "created_at", "updated_at")
