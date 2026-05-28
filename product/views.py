import uuid

from django.db.models import F
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Favourite, Product
from .serializers import (
    FavouriteCreateSerializer,
    FavouriteListSerializer,
    ProductSerializer,
)


def parse_uuid_list(uuid_string):
    if not uuid_string:
        return []

    valid_uuids = []
    for item in uuid_string.split(","):
        try:
            valid_uuids.append(uuid.UUID(item.strip()))
        except ValueError:
            continue
    return valid_uuids


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.select_related("category", "seller").prefetch_related(
            "images"
        )

        uuid_list = parse_uuid_list(self.request.query_params.get("inpk"))
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

        uuid_list = parse_uuid_list(self.request.query_params.get("inpk"))
        if uuid_list:
            qs = qs.filter(pk__in=uuid_list)

        return qs
