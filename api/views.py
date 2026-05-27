from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from category.models import Category
from news.models import News
from product.models import Product

# Yangi serializerimizni import qilamiz
from .serializers import HomePageSerializer


class HomePageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 1. Ma'lumotlarni bazadan optimallashgan holda yig'amiz
        categories = Category.objects.filter(
            parent__isnull=True, 
            is_active=True
        ).order_by('order', 'id')[:10]

        news = News.objects.select_related('author').order_by('-created_at')[:5]

        base_product_qs = Product.objects.filter(
            is_active=True, 
            is_available=True
        ).select_related("category", "seller").prefetch_related("images")

        popular_products = base_product_qs.order_by('-views', '-created_at')[:10]
        new_products = base_product_qs.order_by('-created_at')[:10]

        # 2. Barcha ma'lumotlarni yagona obyektga jamlaymiz
        home_data = {
            "categories": categories,
            "news": news,
            "popular_products": popular_products,
            "new_products": new_products,
        }

        # 3. Yagona serializer orqali validatsiya va serialize qilamiz
        serializer = HomePageSerializer(home_data, context={'request': request})
        return Response(serializer.data)
