from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import UserProfile

User = get_user_model()


# Profile uc serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "first_name",
            "last_name",
            "avatar",
            "gender",
            "birth_date",
            "bio",
        )


# User uc serializer
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "email",
            "user_type",
            "is_verified",
            "profile",
        )


# Register qismi uc - serializer
class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        validators=[
            RegexValidator(r"^\+?\d{9,15}$", "Telefon raqami noto'g'ri formatda.")
        ],
    )
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)


# OTPni tekwiruvci qismi
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(
        min_length=6,
        max_length=6,
        validators=[
            RegexValidator(
                r"^\d{6}$", "OTP kod faqat 6 ta raqamdan iborat bo'lishi kerak."
            )
        ],
    )
