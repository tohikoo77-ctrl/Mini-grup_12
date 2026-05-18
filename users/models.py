import uuid
import random
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.utils import timezone


class UserType(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    USER = "USER", "User"
    SELLER = "SELLER", "Seller"


class GenderType(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)  # Superuser aktiv bo'lishi kerak
        extra_fields.setdefault("user_type", UserType.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        validators=[RegexValidator(r"^\+\d{9,15}$")],
    )
    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    user_type = models.CharField(
        max_length=10, choices=UserType.choices, default=UserType.USER, db_index=True
    )
    is_active = models.BooleanField(default=False, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.phone_number


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", db_index=True
    )
    # Mana bu yerda default='' qo'shildi, migratsiya savol bermasligi uchun:
    first_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/%Y/%m", blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=GenderType.choices, blank=True, null=True, db_index=True
    )
    bio = models.TextField(blank=True, default="")
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.user.phone_number} profile"


def generate_otp():
    return str(random.randint(100000, 999999))


def otp_expiry():
    return timezone.now() + timedelta(minutes=5)


class UserOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="otps", db_index=True
    )
    code = models.CharField(max_length=6, db_index=True)
    is_used = models.BooleanField(default=False, db_index=True)
    expires_at = models.DateTimeField(default=otp_expiry, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.code:
            self.code = generate_otp()
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    def mark_used(self):
        if not self.is_used:
            self.is_used = True
            self.save(update_fields=["is_used"])

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "code"], name="unique_user_otp_code"
            )
        ]
        indexes = [
            models.Index(fields=["user", "code"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_used"]),
        ]

    def __str__(self):
        return f"{self.user.phone_number}-{self.code}"
