from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import News
from .serializers import NewsSerializer


class NewsViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = News.objects.all().order_by("-id")[:5]
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
