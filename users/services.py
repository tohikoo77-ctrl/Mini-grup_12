import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import User, UserOTP


class UserService:
    OTP_LENGTH = 6
    OTP_EXPIRE_MINUTES = 2
    RESEND_COOLDOWN_SECONDS = 30
    MAX_ATTEMPTS = 5

  
    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        return "".join(phone_number.split()).strip()

    @classmethod
    def generate_otp(cls) -> str:
        return "".join(
            str(secrets.randbelow(10))
            for _ in range(cls.OTP_LENGTH)
        )

    @classmethod
    def _get_user(cls, phone_number: str):
        phone_number = cls.normalize_phone(phone_number)
        return User.objects.filter(phone_number=phone_number).first()

    @classmethod
    def get_or_create_user(cls, phone_number: str):
        phone_number = cls.normalize_phone(phone_number)

        user, _ = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                "is_active": False,
                "is_verified": False,
            },
        )
        return user

    @classmethod
    def last_otp(cls, user):
        return (
            user.otps
            .only("created_at")
            .order_by("-created_at")
            .first()
        )

  
    @classmethod
    def send_otp(cls, phone_number: str):
        user = cls.get_or_create_user(phone_number)
        now = timezone.now()

        last = cls.last_otp(user)

        
        if last:
            diff = (now - last.created_at).total_seconds()

            if diff < cls.RESEND_COOLDOWN_SECONDS:
                return {
                    "success": False,
                    "code": "COOLDOWN_ACTIVE",
                    "message": "Please wait before requesting OTP",
                    "data": {
                        "remaining_seconds": int(
                            cls.RESEND_COOLDOWN_SECONDS - diff
                        ),
                    },
                }

        user.otps.filter(
            is_used=False,
            expires_at__gt=now
        ).update(is_used=True)

        otp = UserOTP.objects.create(
            user=user,
            code=cls.generate_otp(),
            expires_at=now + timedelta(minutes=cls.OTP_EXPIRE_MINUTES),
            attempts=0,
        )

        return {
            "success": True,
            "code": "OTP_SENT",
            "message": "OTP sent successfully",
            "data": {
                "otp_id": str(otp.id),
                "expires_in_seconds": cls.OTP_EXPIRE_MINUTES * 60,
            },
        }

   
    @classmethod
    @transaction.atomic
    def verify_otp(cls, phone_number: str, code: str):
        now = timezone.now()
        phone_number = cls.normalize_phone(phone_number)

        user = cls._get_user(phone_number)

        if not user:
            return {
                "success": False,
                "code": "USER_NOT_FOUND",
                "message": "User does not exist",
                "data": {},
            }

       
        otp = (
            user.otps
            .select_for_update()
            .filter(is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return {
                "success": False,
                "code": "OTP_NOT_FOUND",
                "message": "OTP does not exist or already used",
                "data": {},
            }

      
        if otp.expires_at <= now:
            return {
                "success": False,
                "code": "OTP_EXPIRED",
                "message": "OTP expired",
                "data": {},
            }

        
        if otp.is_used:
            return {
                "success": False,
                "code": "OTP_ALREADY_USED",
                "message": "OTP already used",
                "data": {},
            }

        
        if otp.attempts >= cls.MAX_ATTEMPTS:
            return {
                "success": False,
                "code": "MAX_ATTEMPTS_REACHED",
                "message": "Too many attempts",
                "data": {},
            }

       
        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])

            return {
                "success": False,
                "code": "OTP_INVALID",
                "message": "Incorrect OTP",
                "data": {
                    "attempts_left": max(
                        0,
                        cls.MAX_ATTEMPTS - otp.attempts
                    ),
                },
            }


        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user.is_active = True
        user.is_verified = True
        user.save(update_fields=["is_active", "is_verified"])

        return {
            "success": True,
            "code": "VERIFIED",
            "message": "User verified successfully",
            "data": {
                "user_id": str(user.id),
                "phone_number": user.phone_number,
            },
        }
    