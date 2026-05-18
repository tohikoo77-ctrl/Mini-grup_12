from django.urls import path
from .views import OrderViewSet

order_list = OrderViewSet.as_view(
    {
        "get": "list",
    }
)

order_create = OrderViewSet.as_view({"post": "checkout"})

order_detail = OrderViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

order_add_item = OrderViewSet.as_view({"post": "add_item"})

order_apply_promo = OrderViewSet.as_view({"post": "apply_promocode"})

order_cancel = OrderViewSet.as_view({"post": "cancel"})

order_my_orders = OrderViewSet.as_view({"get": "my_orders"})


urlpatterns = [
    path("orders/", order_list, name="order-list"),
    path("orders/create/", order_create, name="order-create"),
    path("orders/<uuid:pk>/", order_detail, name="order-detail"),
    path("orders/<uuid:pk>/add-item/", order_add_item, name="order-add-item"),
    path("orders/<uuid:pk>/apply-promo/", order_apply_promo, name="order-apply-promo"),
    path("orders/<uuid:pk>/cancel/", order_cancel, name="order-cancel"),
    path("orders/my-orders/", order_my_orders, name="order-my-orders"),
]
