from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsViewSet

router = DefaultRouter()

# SLASHNI OLIB TASHLANG: "news/" emas, "news" bo'lishi kerak
router.register("news", NewsViewSet, basename="news")

urlpatterns = [
    path("", include(router.urls)),
]
