from django.urls import path
from .views import CartViewSet

# ViewSet metodlarini HTTP amallariga bog'laymiz
my_cart = CartViewSet.as_view({"get": "my_cart"})  # Savatni ko'rish

add_item = CartViewSet.as_view({"post": "add_item"})  # Mahsulot qo'shish

remove_item = CartViewSet.as_view({"delete": "remove_item"})  # Mahsulotni o'chirish

update_item = CartViewSet.as_view({"patch": "update_item"})  # Miqdorni o'zgartirish

urlpatterns = [
    # GET {{url}}card/my/
    path("my/", my_cart, name="my-cart"),
    # POST {{url}}card/add/
    path("add/", add_item, name="cart-add-item"),
    # DELETE {{url}}card/remove/
    path("remove/", remove_item, name="cart-remove-item"),
    # PATCH {{url}}card/update/
    path("update/", update_item, name="cart-update-item"),
]
