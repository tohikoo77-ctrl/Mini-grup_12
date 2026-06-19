import uuid

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .serializers import (
    LoginSerializer,
    PhoneNumberSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from .services import UserService

User = get_user_model()
ID_NOT_FOUND_MESSAGE = "bunday id mavjut emas."


def api_response(success=True, message="", data=None, status_code=200):
    return Response(
        {
            "success": success,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def otp_response(phone_number, success_code):
    result = UserService.send_otp(phone_number)
    data = result.get("data", {})

    if not result.get("success"):
        return Response(
            {
                "status": "error",
                "code": result.get("code"),
                "message": result.get("message"),
                "phone_number": phone_number,
                "remaining": data.get("remaining_seconds"),
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return Response(
        {
            "status": "success",
            "code": success_code,
            "phone_number": phone_number,
            "expires_in": data.get("expires_in_seconds"),
            "email_sent": data.get("email_sent", False),
            "email_to": data.get("email_to"),
            "email_error": data.get("email_error"),
            "email_detail": data.get("email_detail"),
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

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return otp_response(user.phone_number, "OTP_SENT")


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)

        return api_response(
            success=True,
            message="LOGIN_SUCCESS",
            data={
                **tokens,
                "user": UserSerializer(user).data,
            },
            status_code=status.HTTP_200_OK,
        )


class SendOTPView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return otp_response(serializer.validated_data["phone_number"], "OTP_SENT")


class ResendOTPView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return otp_response(serializer.validated_data["phone_number"], "OTP_RESENT")


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp_code = serializer.validated_data["otp_code"]
        result = UserService.verify_otp(phone_number=phone_number, code=otp_code)

        if not result["success"]:
            return api_response(
                success=False,
                message=result["message"],
                data=result.get("data"),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = UserService._get_user(phone_number)
        tokens = get_tokens_for_user(user)

        return api_response(
            success=True,
            message="LOGIN_SUCCESS",
            data={
                **tokens,
                "user": UserSerializer(user).data,
            },
            status_code=status.HTTP_200_OK,
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
