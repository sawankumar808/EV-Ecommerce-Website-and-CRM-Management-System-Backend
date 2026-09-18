from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    PublicProductViewSet,
    VendorProductPriceViewSet,
)

router = DefaultRouter()

router.register("", ProductViewSet, basename="products")
router.register(
    "public-products",
    PublicProductViewSet,
    basename="public-products"
)
router.register(
    "vendor-product-prices",
    VendorProductPriceViewSet,
    basename="vendor-product-prices"
)

urlpatterns = router.urls