from django.urls import path
from .views import CartViewSet

# Views bog'lanmalari
my_cart_id_bilan = CartViewSet.as_view({"get": "my_cart"})      # ID bilan bittasi
my_cart_hammasi = CartViewSet.as_view({"get": "my_cart_list"})  # ID'siz hammasi

cart_item_detail = CartViewSet.as_view({"get": "cart_item_detail"})
add_item = CartViewSet.as_view({"post": "add_item"})
checkout = CartViewSet.as_view({"post": "checkout"})
remove_item = CartViewSet.as_view({"delete": "remove_item"})
update_item = CartViewSet.as_view({"patch": "update_item"})
clear_cart = CartViewSet.as_view({"delete": "clear"})

urlpatterns = [
    # 1. Hammasini ko'rish (ID'siz): /api/card/my/
    path("my/", my_cart_hammasi, name="my-cart-list"),
    
    # 2. Faqat bittasini ID bilan ko'rish: /api/card/my/<str:pk>/
    path("my/<str:pk>/", my_cart_id_bilan, name="my-cart-detail"),
    
    path("item/<str:item_id>/", cart_item_detail, name="cart-item-detail"),
    path("add/", add_item, name="cart-add-item"),
    path("remove/", remove_item, name="cart-remove-item"),
    path("update/", update_item, name="cart-update-item"),
    path("clear/", clear_cart, name="cart-clear"),
    path("checkout/", checkout, name="cart-checkout"),
]
