import random
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from .models import User, UserOTP


class OTPService:

    OTP_EXPIRE_MINUTES = 2
    RESEND_COOLDOWN_SECONDS = 30

    @staticmethod
    def generate_otp_code():
        return str(random.randint(100000, 999999))

    @classmethod
    def send_otp(cls, phone_number):

        user, _ = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                "is_active": True,
                "is_verified": False,
            },
        )


        user.otps.filter(is_used=False).update(is_used=True)

        last_otp = (
            user.otps
            .filter(is_used=False)
            .order_by("-created_at")
            .first()
        )

        if last_otp:
            diff = (timezone.now() - last_otp.created_at).total_seconds()
            if diff < cls.RESEND_COOLDOWN_SECONDS:
                return user

        code = cls.generate_otp_code()

        UserOTP.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=cls.OTP_EXPIRE_MINUTES),
        )

        print(f"[OTP] {phone_number}: {code}")

        return user

    @staticmethod
    @transaction.atomic
    def verify_otp(user, code):

        otp = (
            user.otps
            .filter(code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return False

        if otp.is_expired():
            return False

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        return True