import re

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from .models import UserOTP, UserProfile

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


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[clean_phone])


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    gmail = serializers.EmailField(source="user.gmail", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user_id",
            "phone_number",
            "gmail",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
        )


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()

    def _get_profile(self, obj):
        try:
            return obj.profile
        except UserProfile.DoesNotExist:
            return None

    def get_first_name(self, obj):
        profile = self._get_profile(obj)
        return profile.first_name if profile else ""

    def get_last_name(self, obj):
        profile = self._get_profile(obj)
        return profile.last_name if profile else ""

    def get_gender(self, obj):
        profile = self._get_profile(obj)
        return profile.gender if profile else None

    def get_birth_date(self, obj):
        profile = self._get_profile(obj)
        return profile.birth_date if profile else None

    def get_bio(self, obj):
        profile = self._get_profile(obj)
        return profile.bio if profile else ""

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "gmail",
            "gender",
            "birth_date",
            "bio",
            "user_type",
            "is_active",
            "is_verified",
        )


class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[clean_phone])
    gmail = serializers.EmailField(required=True, allow_blank=False, allow_null=False)

    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    gender = serializers.ChoiceField(
        choices=[("MALE", "Male"), ("FEMALE", "Female")],
        required=False,
        allow_null=True,
    )
    birth_date = serializers.DateField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "phone_number",
            "gmail",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
        )

    def validate_gmail(self, value):
        value = (value or "").strip().lower()
        if User.objects.filter(gmail__iexact=value).exists():
            raise serializers.ValidationError("bu gmail mavjut.")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("bu raqam mavjut.")
        return value

    def create(self, validated_data):
        phone = validated_data["phone_number"]
        gmail = validated_data.get("gmail", None)

        profile_data = {
            "first_name": validated_data.pop("first_name", ""),
            "last_name": validated_data.pop("last_name", ""),
            "gender": validated_data.pop("gender", None),
            "birth_date": validated_data.pop("birth_date", None),
            "bio": validated_data.pop("bio", ""),
        }

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    phone_number=phone,
                    defaults={
                        "gmail": gmail if gmail else None,
                        "is_active": False,
                        "is_verified": False,
                    },
                )

                if not created and gmail:
                    user.gmail = gmail
                    user.save(update_fields=["gmail"])

                UserProfile.objects.update_or_create(user=user, defaults=profile_data)
        except IntegrityError as exc:
            message = str(exc).lower()
            if "gmail" in message:
                raise serializers.ValidationError({"gmail": ["bu gmail mavjut."]})
            if "phone_number" in message:
                raise serializers.ValidationError(
                    {"phone_number": ["bu raqam mavjut."]}
                )
            raise

        return user


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[clean_phone])
    otp_code = serializers.CharField(
        required=False,
        allow_blank=False,
        validators=[clean_otp],
    )
    otp = serializers.CharField(
        required=False,
        allow_blank=False,
        write_only=True,
        validators=[clean_otp],
    )

    def validate(self, attrs):
        phone = attrs["phone_number"]
        otp_code = attrs.get("otp_code")
        otp = attrs.get("otp")

        if not otp_code and not otp:
            raise serializers.ValidationError({"code": "OTP_REQUIRED"})

        if otp_code and otp and otp_code != otp:
            raise serializers.ValidationError({"code": "OTP_MISMATCH"})

        code = otp_code or otp

        user = User.objects.filter(phone_number=phone).first()
        if not user:
            raise serializers.ValidationError({"code": "USER_NOT_FOUND"})

        otp_instance = (
            UserOTP.objects.filter(
                user=user,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_instance or otp_instance.is_expired():
            raise serializers.ValidationError({"code": "OTP_INVALID_OR_EXPIRED"})

        attrs["user"] = user
        attrs["otp"] = otp_instance
        attrs["otp_code"] = code
        return attrs
