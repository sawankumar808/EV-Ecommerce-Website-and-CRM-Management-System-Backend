from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BatteryBatchViewSet, BatteryViewSet, public_battery
router=DefaultRouter(); router.register("battery-batches",BatteryBatchViewSet); router.register("batteries",BatteryViewSet)
urlpatterns=router.urls+[path("public-battery/<str:serial>/",public_battery)]
