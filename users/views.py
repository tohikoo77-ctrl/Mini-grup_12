from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile
from .serializers import (
    RegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    UserProfileSerializer,
)
from .services import UserService


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


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        result = UserService.send_otp(user.phone_number)

        return api_response(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            status_code=status.HTTP_201_CREATED,
        )


class ResendOTPView(generics.GenericAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = UserService.send_otp(
            serializer.validated_data["phone_number"]
        )

        status_code = (
            status.HTTP_200_OK
            if result["success"]
            else status.HTTP_429_TOO_MANY_REQUESTS
        )

        return api_response(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            status_code=status_code,
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp_code = serializer.validated_data["otp_code"]

        result = UserService.verify_otp(
            phone_number=phone_number,
            code=otp_code,
        )

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


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    