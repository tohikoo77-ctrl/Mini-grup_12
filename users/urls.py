from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    ResendOTPView,
    VerifyOTPView,
    MeView,
    UserProfileView,
)

app_name = "api"


auth_urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("verify/", VerifyOTPView.as_view(), name="verify_otp"),
]

user_urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]


urlpatterns = [
    path("api/v1/auth/", include((auth_urlpatterns, "auth"), namespace="auth")),
    path("api/v1/user/", include((user_urlpatterns, "user"), namespace="user")),
]
