from django.urls import include, path
from rest_framework import routers

from .views import CartViewSet, OrderViewSet, ProductViewSet

router = routers.DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "cart/",
        CartViewSet.as_view(
            {
                "get": "retrieve",
                "post": "add_item",
                "patch": "adjust_item_quantity",
                "put": "remove_item",
                "delete": "clear_cart",
            }
        ),
        name="cart",
    ),
]
