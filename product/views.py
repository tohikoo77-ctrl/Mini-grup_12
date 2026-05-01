from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import F

from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.select_related(
            "category",
            "seller"
        ).prefetch_related("images")

        # 🔥 FILTER LAYER
        return ProductFilter(qs, self.request.query_params).filter()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # ⚡ SAFE VIEWS INCREMENT (race-safe)
        Product.objects.filter(pk=instance.pk).update(
            views=F("views") + 1
        )

        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    