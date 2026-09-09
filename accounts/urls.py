from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import UserViewSet, SalesTargetViewSet, current_user, sales_team_summary

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("sales-targets", SalesTargetViewSet)
urlpatterns = router.urls + [
    path("auth/me/", current_user, name="current-user"),
    path("sales-team-summary/", sales_team_summary, name="sales-team-summary"),
]
