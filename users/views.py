from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    UserProfileSerializer,
)
from .services import OTPService
from .models import User



class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        OTPService.send_otp(phone_number)

        return Response(
            {
                "message": "Tasdiqlash kodi yuborildi",
                "phone_number": phone_number,
            },
            status=status.HTTP_200_OK,
        )



class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp = serializer.validated_data["otp"]

        OTPService.verify_otp(user, otp.code)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Tasdiqlandi",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )





class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = self.request.user.profile.__class__.objects.get_or_create(
            user=self.request.user
        )
        return profile
    