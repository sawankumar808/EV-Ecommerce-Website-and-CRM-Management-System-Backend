from rest_framework.routers import DefaultRouter
from .views import ScooterViewSet

router = DefaultRouter()
router.register("scooters", ScooterViewSet)
urlpatterns = router.urls
