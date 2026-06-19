from django.urls import path

from .views import (
    LoginView,
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

app_name = "users"

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/otp/send/", SendOTPView.as_view(), name="otp-send"),
    path("auth/otp/resend/", ResendOTPView.as_view(), name="otp-resend"),
    path("auth/otp/verify/", VerifyOTPView.as_view(), name="otp-verify"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/register/", RegisterView.as_view(), name="profile_register"),
    path("profile/<str:pk>/", UserProfileDetailView.as_view(), name="profile_detail"),
    path("profile/", UserProfileListCreateView.as_view(), name="profile_list"),
    path("", UserListView.as_view(), name="list"),
    path("<str:pk>/", UserDetailView.as_view(), name="detail"),
]
