import uuid

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .serializers import (
    PhoneNumberSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from .services import OTPService

User = get_user_model()
ID_NOT_FOUND_MESSAGE = "bunday id mavjut emas."


def otp_response(phone_number, success_code):
    result = OTPService.send_otp(phone_number)

    if result.get("status") == "cooldown":
        return Response(
            {
                "status": "error",
                "code": "OTP_COOLDOWN",
                "phone_number": phone_number,
                "remaining": result["remaining"],
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return Response(
        {
            "status": "success",
            "code": success_code,
            "phone_number": phone_number,
            "expires_in": result.get("expires_in"),
            "email_sent": result.get("email_sent", False),
            "email_to": result.get("email_to"),
            "email_error": result.get("email_error"),
            "email_detail": result.get("email_detail"),
        },
        status=status.HTTP_200_OK,
    )


class CustomIDLookupMixin:
    lookup_field = "pk"

    def get_object(self):
        raw_pk = self.kwargs.get(self.lookup_field)

        try:
            pk = uuid.UUID(str(raw_pk))
        except (TypeError, ValueError):
            raise NotFound(detail=ID_NOT_FOUND_MESSAGE)

        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=pk).first()

        if obj is None:
            raise NotFound(detail=ID_NOT_FOUND_MESSAGE)

        self.check_object_permissions(self.request, obj)
        return obj


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        return otp_response(user.phone_number, "OTP_SENT")


class SendOTPView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        return otp_response(phone, "OTP_SENT")


class ResendOTPView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        return otp_response(phone, "OTP_RESENT")


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp = serializer.validated_data["otp"]

        result = OTPService.verify_and_activate(user, otp)
        if not result["status"]:
            raise ValidationError({"code": result["error"]})

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": "success",
                "code": "LOGIN_SUCCESS",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.select_related("profile").order_by("-created_at")


class UserDetailView(CustomIDLookupMixin, generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.select_related("profile")


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RegisterSerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        return otp_response(user.phone_number, "OTP_SENT")


class UserProfileDetailView(CustomIDLookupMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related("user")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        self.perform_destroy(instance)
        user.delete()

        return Response(
            {"status": "success", "code": "PROFILE_DELETED"},
            status=status.HTTP_204_NO_CONTENT,
        )
