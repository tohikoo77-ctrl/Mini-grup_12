from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import UserProfile, UserOTP
from common.models import UserAddress

User = get_user_model()


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


# Register uc
class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        validators=[
            RegexValidator(r"^\+?\d{9,15}$", "Telefon raqami noto'g'ri formatda.")
        ],
    )
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)

    def create(self, validated_data):
        phone = validated_data["phone_number"]

        user, created = User.objects.get_or_create(
            phone_number=phone, defaults={"email": validated_data.get("email")}
        )

        return user


# OTP
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

    def validate(self, attrs):
        phone = attrs["phone_number"]
        code = attrs["otp_code"]

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("User topilmadi")

        otp = (
            UserOTP.objects.filter(user=user, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            raise serializers.ValidationError("OTP noto‘g‘ri")

        if otp.is_expired():
            raise serializers.ValidationError("OTP eskirgan")

        attrs["user"] = user
        attrs["otp"] = otp

        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]

        otp.mark_used()

        user.is_verified = True
        user.save()

        return user
