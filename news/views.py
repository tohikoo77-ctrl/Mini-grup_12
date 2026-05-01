from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import News
from .serializers import NewsSerializer, NewsCreateUpdateSerializer


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()

    def get_serializer_class(self):
        # Yaratish va tahrirlash uchun maxsus serializer
        if self.action in ["create", "update", "partial_update"]:
            return NewsCreateUpdateSerializer
        return NewsSerializer

    def get_permissions(self):
        # Ko'rish hamma uchun, yaratish va o'zgartirish faqat login qilganlar uchun
        if self.action in ["list", "retrieve", "published", "view"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Muallifni avtomatik tarzda joriy foydalanuvchiga biriktirish
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def view(self, request, pk=None):
        """Yangilik ko'rilganda views sonini oshirish"""
        news = self.get_object()
        news.views += 1
        news.save()
        return Response({"views": news.views}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def published(self, request):
        """Faqat e'lon qilingan yangiliklarni olish"""
        # Modelingizda 'is_active' yoki 'is_published' borligini tekshiring
        data = News.objects.filter(is_active=True)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
