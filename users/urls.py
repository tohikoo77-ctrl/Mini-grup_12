from django.urls import path
from .views import RegisterView, VerifyOTPView, UserProfileUpdateView

urlpatterns = [
    # AUTH - qsmi
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("verify/", VerifyOTPView.as_view(), name="auth-verify"),
    # Profile - qsmi
    path("profile/", UserProfileUpdateView.as_view(), name="profile"),
]
