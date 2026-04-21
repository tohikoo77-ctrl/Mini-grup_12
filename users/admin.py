from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserOTP

# Register your models here.


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"

    fields = (
        "first_name",
        "last_name",
        "avatar",
        "gender",
        "birth_date",
        "bio",
    )


# Admin User
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
    )

    search_fields = (
        "phone_number",
        "email",
    )

    ordering = ("-created_at",)

    inlines = (UserProfileInline,)

    # BaseUserAdmin bilan konflikt bo‘lmasligi uchun togri format
    fieldsets = (
        (
            "Account",
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
                )
            },
        ),
        (
            "Important dates",
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
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
    )


# Admin - OTP
from django.contrib import admin
from .models import UserOTP


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "code",
        "is_used",
        "expires_at",
        "created_at",
    )

    list_filter = ("is_used",)

    search_fields = (
        "user__phone_number",
        "code",
    )

    readonly_fields = ("created_at",)
