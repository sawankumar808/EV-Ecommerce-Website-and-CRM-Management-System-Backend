from django.urls import path
from rest_framework.routers import DefaultRouter
from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets
from .views import (
    LeadSourceViewSet, 
    PipelineStageViewSet, 
    LeadViewSet, 
    FollowUpViewSet,
    QuotationViewSet, 
    QuotationItemViewSet, 
    TaskViewSet, 
    NotificationViewSet,
    dashboard_summary
)

# Sales Persons / Users list ke liye Serializer & ViewSet
class SalesUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class SalesUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SalesUserSerializer

    def get_queryset(self):
        User = get_user_model()
        return User.objects.filter(is_active=True)

router = DefaultRouter()
router.register("lead-sources", LeadSourceViewSet)
router.register("pipeline-stages", PipelineStageViewSet)
router.register("leads", LeadViewSet)
router.register("follow-ups", FollowUpViewSet)
router.register("quotations", QuotationViewSet)
router.register("quotation-items", QuotationItemViewSet)
router.register("tasks", TaskViewSet)
router.register("notifications", NotificationViewSet, basename="notification")

# Register Sales Team Endpoints
router.register("users", SalesUserViewSet, basename="user")
router.register("sales-team", SalesUserViewSet, basename="sales-team")

urlpatterns = router.urls + [
    path("dashboard-summary/", dashboard_summary, name="dashboard-summary"),
]