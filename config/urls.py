from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.views import HomePageView 

urlpatterns = [
    path("api/home/", HomePageView.as_view(), name="home-page"),
    path("admin/", admin.site.urls),
    path("api/user/", include("users.urls")),
    path("api/product/", include("product.urls")),
    path("api/card/", include("cart.urls")),
    path("api/common/", include("common.urls")),
    path("api/category/", include("category.urls")),
    path("api/news/", include("news.urls")),
    path("api/order/", include("order.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
