import random
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from .models import User, UserOTP


class OTPService:

    @staticmethod
    def generate_otp_code():
        return str(random.randint(100000, 999999))

    @classmethod
    def send_otp(cls, phone_number):

        user, _ = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={"is_active": True, "is_verified": False},
        )

        # eski OTPlarni disable qilish
        user.otps.filter(is_used=False).update(is_used=True)

        # spam protection (30 sec cooldown)
        last_otp = user.otps.order_by("-created_at").first()
        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < 30:
            return user

        code = cls.generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=2)

        UserOTP.objects.create(user=user, code=code, expires_at=expires_at)

        # SMS integration (hozircha mock)
        print(f"--- SMS SENT TO {phone_number}: {code} ---")

        return user

    @staticmethod
    @transaction.atomic
    def verify_otp(user, code):

        otp = user.otps.filter(code=code, is_used=False).order_by("-created_at").first()

        if not otp:
            return False

        if otp.is_expired():
            return False

        if otp.mark_used():
            user.is_verified = True
            user.save(update_fields=["is_verified"])
            return True

        return False
