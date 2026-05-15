from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from .models import Product, Favourite
from .serializers import ProductSerializer, FavouriteListSerializer, FavouriteCreateSerializer
from .filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.select_related(
            "category",
            "seller"
        ).prefetch_related("images")

       
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
    

class FavouriteViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
   
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  

    def get_serializer_class(self):
        if self.action == 'create':
            return FavouriteCreateSerializer
        return FavouriteListSerializer

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user).select_related(
            'product', 'product__category', 'product__seller'
        ).prefetch_related('product__images')
