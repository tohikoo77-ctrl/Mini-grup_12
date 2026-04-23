from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"
        read_only_fields = ("views", "author")


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"
