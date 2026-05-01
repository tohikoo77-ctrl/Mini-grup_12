from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = News
        fields = "__all__"
        read_only_fields = ("views", "author", "slug", "created_at")


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        # УДАЛИЛИ is_active, так как его нет в модели.
        # Также убрали author, так как он заполняется в views.py
        fields = ("title", "content", "category", "image")
