from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, PublicProductViewSet, VendorProductPriceViewSet

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("public-products", PublicProductViewSet, basename="public-products")
router.register("vendor-product-prices", VendorProductPriceViewSet)
urlpatterns = router.urls
