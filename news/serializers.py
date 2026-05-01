from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = News
        fields = "__all__"
        read_only_fields = ("views", "author", "slug", "created_at")


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ("title", "content", "category", "image") 
