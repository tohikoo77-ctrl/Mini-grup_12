from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, UserProfile, UserOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # BaseUserAdmin formalaridagi email talablarini chetlab o'tamiz
    form = BaseUserAdmin.form
    add_form = BaseUserAdmin.add_form

    # email -> gmail deb o'zgartirildi
    list_display = (
        "phone_number",
        "gmail",
        "user_type",
        "is_verified",
        "is_active",
        "is_staff",
        "created_at",
    )

    list_filter = (
        "user_type",
        "is_verified",
        "is_active",
        "is_staff",
        "created_at",
    )

    # email -> gmail deb o'zgartirildi
    search_fields = (
        "phone_number",
        "gmail",
    )

    ordering = ("-created_at",)

    list_per_page = 25
    date_hierarchy = "created_at"

    list_select_related = ("profile",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
    )

    # email -> gmail deb o'zgartirildi
    fieldsets = (
        (
            "Account Info",
            {
                "fields": (
                    "phone_number",
                    "gmail",
                    "password",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "user_type",
                    "is_verified",
                    "is_active",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # email -> gmail deb o'zgartirildi
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "gmail",
                    "password1",
                    "password2",
                    "user_type",
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("profile")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "full_name",
        "gender",
        "avatar_preview",
        "created_at",
    )

    list_filter = (
        "gender",
        "created_at",
    )

    search_fields = (
        "user__phone_number",
        "first_name",
        "last_name",
    )

    ordering = ("-created_at",)

    list_per_page = 25

    list_select_related = ("user",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "avatar_preview",
    )

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Profile Info", {
            "fields": ("first_name", "last_name", "gender", "bio", "birth_date")
        }),
        ("Media", {"fields": ("avatar", "avatar_preview")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def full_name(self, obj):
        return obj.full_name or "-"

    full_name.short_description = "Full Name"

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;border-radius:50%;object-fit:cover;" />',
                obj.avatar.url,
            )
        return "—"

    avatar_preview.short_description = "Avatar"


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "code",
        "status",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "is_used",
        "expires_at",
        "created_at",
    )

    search_fields = (
        "user__phone_number",
        "code",
    )

    ordering = ("-created_at",)

    list_per_page = 25

    list_select_related = ("user",)

    readonly_fields = (
        "user",
        "code",
        "expires_at",
        "created_at",
        "status",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def status(self, obj):
        if obj.is_used:
            return "USED"
        if obj.is_expired():
            return "EXPIRED"
        return "ACTIVE"

    status.short_description = "Status"
    