from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, 
    VerifyOTPView, 
    UserProfileViewSet,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/verify/", VerifyOTPView.as_view(), name="auth-verify"),
    path("", include(router.urls)),
]
