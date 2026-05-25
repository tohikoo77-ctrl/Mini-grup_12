from django.urls import path

from .views import CartViewSet

# ViewSet metodlarini HTTP amallariga bog'laymiz
cart_list = CartViewSet.as_view({"get": "list"})
cart_detail = CartViewSet.as_view({"get": "retrieve"})
my_cart = CartViewSet.as_view({"get": "my_cart"})
add_item = CartViewSet.as_view({"post": "add_item"})
checkout = CartViewSet.as_view({"post": "checkout"})
remove_item = CartViewSet.as_view({"delete": "remove_item"})
update_item = CartViewSet.as_view({"patch": "update_item"})
clear_cart = CartViewSet.as_view({"delete": "clear"})

urlpatterns = [
    # GET /api/card/ — savatlar ro'yxati (?id=<uuid>)
    path("", cart_list, name="cart-list"),
    # Aniq yo'llar UUID detail dan oldin bo'lishi kerak
    path("my/", my_cart, name="my-cart"),
    path("add/", add_item, name="cart-add-item"),
    path("remove/", remove_item, name="cart-remove-item"),
    path("update/", update_item, name="cart-update-item"),
    path("clear/", clear_cart, name="cart-clear"),
    path("checkout/", checkout, name="cart-checkout"),
    # GET /api/card/<uuid>/ — bitta savat ID bo'yicha
    path("<uuid:pk>/", cart_detail, name="cart-detail"),
]
