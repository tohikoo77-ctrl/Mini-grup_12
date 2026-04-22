from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserOTP




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

# Togri formatda koriniwi uc
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
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
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
        "last_login",
    )


#OTP 
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
