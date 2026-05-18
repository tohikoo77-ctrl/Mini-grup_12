import re
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile, UserOTP
from common.models import UserAddress

User = get_user_model()

PHONE_REGEX = re.compile(r"^\+\d{9,15}$")
OTP_REGEX = re.compile(r"^\d{6}$")


def clean_phone(value):
    value = re.sub(r"\s+", "", (value or "").strip())
    if not PHONE_REGEX.match(value):
        raise serializers.ValidationError({"code": "INVALID_PHONE"})
    return value


def clean_otp(value):
    value = (value or "").strip()
    if not OTP_REGEX.match(value):
        raise serializers.ValidationError({"code": "INVALID_OTP"})
    return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "first_name", "last_name", "gender", "birth_date", "bio")


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = (
            "id",
            "country",
            "region",
            "city",
            "street",
            "house",
            "postal_code",
            "is_default",
        )


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    addresses = UserAddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "email",
            "user_type",
            "is_verified",
            "profile",
            "addresses",
        )


class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[clean_phone])
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("phone_number", "email")

    def validate_email(self, value):
        return (value or "").strip().lower()

    def create(self, validated_data):
        phone = validated_data["phone_number"]

        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "email": validated_data.get("email", ""),
                "is_active": False,
                "is_verified": False,
            },
        )

        if not created and validated_data.get("email"):
            user.email = validated_data["email"]
            user.save(update_fields=["email"])

        return user


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[clean_phone])


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[clean_phone])
    otp_code = serializers.CharField(validators=[clean_otp])

    def validate(self, attrs):
        phone = attrs["phone_number"]
        code = attrs["otp_code"]

        user = User.objects.filter(phone_number=phone).first()
        if not user:
            raise serializers.ValidationError({"code": "USER_NOT_FOUND"})

        otp = (
            UserOTP.objects.filter(
                user=user,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if not otp or otp.is_expired() or otp.is_used:
            raise serializers.ValidationError({"code": "OTP_INVALID_OR_EXPIRED"})

        attrs["user"] = user
        attrs["otp"] = otp
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]

        with transaction.atomic():
            otp.is_used = True
            otp.save(update_fields=["is_used"])

            user.is_verified = True
            user.is_active = True
            user.save(update_fields=["is_verified", "is_active"])

        return user
