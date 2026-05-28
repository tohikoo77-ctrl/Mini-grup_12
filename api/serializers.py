from rest_framework import serializers

# Mavjud serializerlarni import qilamiz
from category.serializers import CategoryListSerializer
from news.serializers import NewsSerializer
from product.serializers import ProductSerializer


class HomePageSerializer(serializers.Serializer):
    """
    Bosh sahifadagi barcha bloklarni yagona tuzilmaga 
    birlashtiruvchi kompozit (birlashgan) serializer.
    """
    categories = CategoryListSerializer(many=True, read_only=True)
    news = NewsSerializer(many=True, read_only=True)
    popular_products = ProductSerializer(many=True, read_only=True)
    new_products = ProductSerializer(many=True, read_only=True)
