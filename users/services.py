import secrets
from datetime import timedelta

<<<<<<< HEAD
=======
from django.conf import settings
from django.core.mail import send_mail
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
from django.db import transaction
from django.utils import timezone

from .models import User, UserOTP


class UserService:
    OTP_LENGTH = 6
    OTP_EXPIRE_MINUTES = 2
    RESEND_COOLDOWN_SECONDS = 30
<<<<<<< HEAD
    MAX_ATTEMPTS = 5
=======
    EMAIL_PLACEHOLDERS = {
        "",
        "yourgmail@gmail.com",
        "your_google_app_password",
        "google_app_password",
    }
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c

  
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

    @staticmethod
    def send_otp_email(user, code):
        if not user.gmail:
            return {"sent": False, "to": None, "error": "USER_GMAIL_NOT_FOUND"}

        email_user = (settings.EMAIL_HOST_USER or "").strip()
        email_password = (settings.EMAIL_HOST_PASSWORD or "").strip()

        if settings.EMAIL_BACKEND.endswith(".smtp.EmailBackend") and (
            email_user in OTPService.EMAIL_PLACEHOLDERS
            or email_password in OTPService.EMAIL_PLACEHOLDERS
        ):
            return {
                "sent": False,
                "to": user.gmail,
                "error": "EMAIL_SMTP_NOT_CONFIGURED",
            }

        try:
            sent_count = send_mail(
                subject="Verify code",
                message=(
                    "Assalomu alaykum!\n\n"
                    f"Sizning verification codingiz: {code}\n"
                    f"Bu kod {OTPService.OTP_EXPIRE_MINUTES} daqiqa amal qiladi.\n\n"
                    "Agar bu so'rovni siz yubormagan bo'lsangiz, xabarni e'tiborsiz qoldiring."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.gmail],
                fail_silently=False,
            )
        except Exception as exc:
            return {
                "sent": False,
                "to": user.gmail,
                "error": "EMAIL_SEND_FAILED",
                "detail": str(exc),
            }

        return {
            "sent": sent_count > 0,
            "to": user.gmail,
            "error": None if sent_count > 0 else "EMAIL_NOT_SENT",
        }

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
        email_result = cls.send_otp_email(user, code)

        return {
<<<<<<< HEAD
            "success": True,
            "code": "OTP_SENT",
            "message": "OTP sent successfully",
            "data": {
                "otp_id": str(otp.id),
                "expires_in_seconds": cls.OTP_EXPIRE_MINUTES * 60,
            },
=======
            "status": "sent",
            "expires_in": cls.OTP_EXPIRE_MINUTES * 60,
            "email_sent": email_result["sent"],
            "email_to": email_result["to"],
            "email_error": email_result["error"],
            "email_detail": email_result.get("detail"),
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
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

<<<<<<< HEAD
        return {
            "success": True,
            "code": "VERIFIED",
            "message": "User verified successfully",
            "data": {
                "user_id": str(user.id),
                "phone_number": user.phone_number,
            },
        }
    
=======
        return {"status": True, "message": "VERIFIED"}

    @staticmethod
    @transaction.atomic
    def verify_and_activate(user, otp):
        otp = (
            UserOTP.objects.select_for_update()
            .filter(pk=otp.pk, user=user)
            .first()
        )

        if not otp:
            return {"status": False, "error": "OTP_NOT_FOUND"}

        if otp.is_used:
            return {"status": False, "error": "OTP_ALREADY_USED"}

        if otp.is_expired():
            return {"status": False, "error": "OTP_EXPIRED"}

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user.is_active = True
        user.is_verified = True
        user.save(update_fields=["is_active", "is_verified"])

        return {"status": True, "message": "VERIFIED"}
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
