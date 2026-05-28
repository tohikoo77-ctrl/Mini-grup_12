<<<<<<< HEAD
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
=======
import uuid
from django.db.models import F
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Product, Favourite
from .serializers import ProductSerializer, FavouriteListSerializer, FavouriteCreateSerializer


def parse_uuid_list(uuid_string):
    """
    Vergul bilan ajratilgan UUID qatorini toza UUID obyektlari ro'yxatiga o'tkazadi.
    Noto'g'ri qiymatlarni o'tkazib yuboradi (baza xatolik bermasligi uchun).
    """
    if not uuid_string:
        return []
        
    valid_uuids = []
    for item in uuid_string.split(','):
        cleaned_item = item.strip()
        try:
            valid_uuids.append(uuid.UUID(cleaned_item))
        except ValueError:
            continue
            
    return valid_uuids


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.select_related(
            "category",
            "seller",
        ).prefetch_related("images")

        # ?inpk=uuid1,uuid2 parametrini tekshiramiz
        inpk = self.request.query_params.get('inpk')
        uuid_list = parse_uuid_list(inpk)
        
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)

        return ProductFilter(qs, self.request.query_params).filter()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        Product.objects.filter(pk=instance.pk).update(views=F("views") + 1)
        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FavouriteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "create":
            return FavouriteCreateSerializer
        return FavouriteListSerializer

    def get_queryset(self):
        qs = Favourite.objects.filter(user=self.request.user).select_related(
            "product", "product__category", "product__seller"
        ).prefetch_related("product__images")

        # ?inpk=uuid1,uuid2 parametrini tekshiramiz (Favourite obyektining o'z IDsi bo'yicha)
        inpk = self.request.query_params.get('inpk')
        uuid_list = parse_uuid_list(inpk)
        
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)
            
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
