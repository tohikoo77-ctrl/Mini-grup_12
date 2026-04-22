from django.urls import path
from .views import RegisterView, VerifyOTPView, UserProfileUpdateView


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/verify/", VerifyOTPView.as_view(), name="auth-verify"),

    path("profile/", UserProfileUpdateView.as_view(), name="profile"),
]