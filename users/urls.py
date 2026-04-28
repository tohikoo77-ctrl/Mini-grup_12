from django.urls import path
from .views import (
    RegisterView,
    VerifyOTPView,
    UserProfileUpdateView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/verify/", VerifyOTPView.as_view(), name="auth-verify"),
    path('profile/', UserProfileUpdateView.as_view(), name='profile'),
]
