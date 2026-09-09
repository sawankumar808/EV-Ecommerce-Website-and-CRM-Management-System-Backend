from rest_framework.routers import DefaultRouter
from .views import CouponViewSet

router = DefaultRouter()
router.register("coupons", CouponViewSet)
urlpatterns = router.urls
