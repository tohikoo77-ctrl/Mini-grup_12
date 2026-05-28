from django.urls import path

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

app_name = "users"

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/otp/resend/", ResendOTPView.as_view(), name="otp-resend"),
    path("auth/otp/verify/", VerifyOTPView.as_view(), name="otp-verify"),

<<<<<<< HEAD
=======
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
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
    path("me/", MeView.as_view(), name="me"),
    path("profile/register/", RegisterView.as_view(), name="profile_register"),
    path("profile/<str:pk>/", UserProfileDetailView.as_view(), name="profile_detail"),
    path("profile/", UserProfileListCreateView.as_view(), name="profile_list"),
    path("<str:pk>/", UserDetailView.as_view(), name="detail"),
]
