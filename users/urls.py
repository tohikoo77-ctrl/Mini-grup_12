from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    MeView,
    RegisterView,
    ResendOTPView,
    SendOTPView,
    UserDetailView,
    UserListView,
    UserProfileDetailView,
    UserProfileListCreateView,
    VerifyOTPView,
)

app_name = "api"


auth_urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("verify/", VerifyOTPView.as_view(), name="verify_otp"),
]

user_urlpatterns = [
    path("", UserListView.as_view(), name="list"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/register/", RegisterView.as_view(), name="profile_register"),
    path("profile/<str:pk>/", UserProfileDetailView.as_view(), name="profile_detail"),
    path("profile/", UserProfileListCreateView.as_view(), name="profile_list"),
    path("<str:pk>/", UserDetailView.as_view(), name="detail"),
]


urlpatterns = [
    path("api/v1/auth/", include((auth_urlpatterns, "auth"), namespace="auth")),
    path("api/v1/user/", include((user_urlpatterns, "user"), namespace="user")),
]
