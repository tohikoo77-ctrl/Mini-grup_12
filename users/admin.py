from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile, UserOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        "phone_number",
        "email",
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

    search_fields = (
        "phone_number",
        "email",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
    )

    fieldsets = (
        (
            "Account Info",
            {
                "fields": (
                    "phone_number",
                    "email",
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

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "email",
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

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    list_per_page = 25
    date_hierarchy = "created_at"
    show_full_result_count = True


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "first_name",
        "last_name",
        "gender",
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

    readonly_fields = ("created_at",)

    list_per_page = 25

    list_select_related = ("user",)


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "code",
        "is_used",
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

    readonly_fields = (
        "code",
        "created_at",
        "expires_at",
    )

    list_per_page = 25
    date_hierarchy = "created_at"
    list_select_related = ("user",)
