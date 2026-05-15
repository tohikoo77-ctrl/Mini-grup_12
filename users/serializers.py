import re

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers

from common.models import UserAddress
from .models import UserProfile
from .services import UserService

User = get_user_model()

PHONE_REGEX = re.compile(r"^\+\d{9,15}$")
OTP_REGEX = re.compile(r"^\d{6}$")


def clean_phone(value):
    value = re.sub(r"\s+", "", (value or "").strip())

    if not PHONE_REGEX.match(value):
        raise serializers.ValidationError({
            "code": "INVALID_PHONE",
            "message": "Phone format is invalid",
        })

    return value


def clean_otp(value):
    value = (value or "").strip()

    if not OTP_REGEX.match(value):
        raise serializers.ValidationError({
            "code": "INVALID_OTP",
            "message": "OTP format is invalid",
        })

    return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
        )


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
        phone_number = validated_data["phone_number"]
        email = validated_data.get("email", "")

        try:
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    "email": email,
                    "is_active": False,
                    "is_verified": False,
                },
            )
        except IntegrityError:
            raise serializers.ValidationError({
                "code": "USER_CREATION_FAILED",
                "message": "User creation conflict",
            })

        if not created and email and user.email != email:
            user.email = email

            try:
                user.save(update_fields=["email"])
            except IntegrityError:
                raise serializers.ValidationError({
                    "code": "EMAIL_ALREADY_EXISTS",
                    "message": "Email already taken",
                })

        return user


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[clean_phone])


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[clean_phone])
    otp_code = serializers.CharField(validators=[clean_otp])

    def validate(self, attrs):
        phone_number = attrs["phone_number"]

        user = UserService.get_user(phone_number)

        if not user:
            raise serializers.ValidationError({
                "code": "USER_NOT_FOUND",
                "message": "User does not exist",
            })

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        code = self.validated_data["otp_code"]

        result = UserService.verify_otp(
            phone_number=user.phone_number,
            code=code,
        )

        if not result["success"]:
            raise serializers.ValidationError({
                "code": result.get("code", "OTP_ERROR"),
                "message": result.get("message", "OTP verification failed"),
            })

        return user
    