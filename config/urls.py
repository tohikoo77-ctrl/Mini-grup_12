from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("users.urls")),
    path("api/product/", include("product.urls")),
    path("api/card/", include("cart.urls")),
    path("api/common/", include("common.urls")),
    path("api/category/", include("category.urls")),
    path("api/news/", include("news.urls")),
    path("api/order/", include("order.urls")),
]
