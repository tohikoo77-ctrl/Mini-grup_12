import secrets
from datetime import timedelta

from django.utils import timezone
from django.db import transaction

from .models import User, UserOTP


class OTPService:
    OTP_LENGTH = 6
    OTP_EXPIRE_MINUTES = 2
    RESEND_COOLDOWN_SECONDS = 30

    @staticmethod
    def generate_code():
        return "".join(str(secrets.randbelow(10)) for _ in range(OTPService.OTP_LENGTH))

    @staticmethod
    def _get_or_create_user(phone_number):
        user, _ = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                "is_active": False,
                "is_verified": False,
            },
        )
        return user

    @classmethod
    def send_otp(cls, phone_number):
        user = cls._get_or_create_user(phone_number)
        now = timezone.now()

        last_otp = user.otps.order_by("-created_at").only("created_at").first()

        if last_otp:
            seconds_passed = (now - last_otp.created_at).total_seconds()
            remaining = cls.RESEND_COOLDOWN_SECONDS - int(seconds_passed)

            if remaining > 0:
                return {
                    "status": "cooldown",
                    "remaining": remaining,
                }

        user.otps.filter(is_used=False, expires_at__gt=now).update(is_used=True)

        code = cls.generate_code()

        UserOTP.objects.create(
            user=user,
            code=code,
            expires_at=now + timedelta(minutes=cls.OTP_EXPIRE_MINUTES),
        )

        return {
            "status": "sent",
            "expires_in": cls.OTP_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    @transaction.atomic
    def verify(user, code):
        otp = (
            user.otps.select_for_update()
            .filter(code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return {"status": False, "error": "OTP_NOT_FOUND"}

        if otp.is_expired():
            return {"status": False, "error": "OTP_EXPIRED"}

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user.is_active = True
        user.is_verified = True
        user.save(update_fields=["is_active", "is_verified"])

        return {"status": True, "message": "VERIFIED"}
