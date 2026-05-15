from django.urls import path

from .views import (
    RegisterView,
    ResendOTPView,
    VerifyOTPView,
    MeView,
    UserProfileView,
)

app_name = "users"

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/otp/resend/", ResendOTPView.as_view(), name="otp-resend"),
    path("auth/otp/verify/", VerifyOTPView.as_view(), name="otp-verify"),

    path("me/", MeView.as_view(), name="me"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]
