from django.urls import path
from .views import ProductViewSet, FavouriteViewSet


product_list = ProductViewSet.as_view({"get": "list", "post": "create"})

product_detail = ProductViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

product_my = ProductViewSet.as_view({"get": "my_products"})

favourite_list = FavouriteViewSet.as_view({"get": "list", "post": "create"})

favourite_detail = FavouriteViewSet.as_view({"delete": "destroy"})

favourite_my = FavouriteViewSet.as_view({"get": "my_favourites"})


urlpatterns = [
    path("products/", product_list, name="product-list"),
    path("products/<uuid:pk>/", product_detail, name="product-detail"),
    path("products/my/", product_my, name="product-my"),
    path("favourites/", favourite_list, name="favourite-list"),
    path("favourites/<uuid:pk>/", favourite_detail, name="favourite-detail"),
    path("favourites/my/", favourite_my, name="favourite-my"),
]
