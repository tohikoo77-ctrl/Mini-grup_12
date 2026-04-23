from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import News
from .serializers import NewsSerializer, NewsCreateUpdateSerializer

# Create your views here.


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return NewsCreateUpdateSerializer
        return NewsSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def view(self, request, pk=None):
        news = self.get_object()
        news.views += 1
        news.save()
        return Response({"views": news.views})

    @action(detail=False, methods=["get"])
    def published(self, request):
        data = News.objects.filter(is_published=True)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
