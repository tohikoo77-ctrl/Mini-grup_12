from django.urls import path

from .views import CartViewSet

my_cart = CartViewSet.as_view({"get": "my_cart"})
add_item = CartViewSet.as_view({"post": "add_item"})
checkout = CartViewSet.as_view({"post": "checkout"})
remove_item = CartViewSet.as_view({"delete": "remove_item"})
update_item = CartViewSet.as_view({"patch": "update_item"})
clear_cart = CartViewSet.as_view({"delete": "clear"})

urlpatterns = [
    path("my/", my_cart, name="my-cart"),
    path("add/", add_item, name="cart-add-item"),
    path("remove/", remove_item, name="cart-remove-item"),
    path("update/", update_item, name="cart-update-item"),
    path("clear/", clear_cart, name="cart-clear"),
    path("checkout/", checkout, name="cart-checkout"),
]
