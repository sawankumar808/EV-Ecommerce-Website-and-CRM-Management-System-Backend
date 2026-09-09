from django.utils import timezone
from django.db.models import Sum, Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import (
    LeadSource, PipelineStage, Lead, LeadNote, LeadActivity, FollowUp,
    Quotation, QuotationItem, Task, TaskComment, Notification,
)
from .serializers import (
    LeadSourceSerializer, PipelineStageSerializer, LeadSerializer, LeadDetailSerializer,
    LeadNoteSerializer, FollowUpSerializer, QuotationSerializer, QuotationItemSerializer,
    TaskSerializer, TaskCommentSerializer, NotificationSerializer,
)
from customers.models import Customer


class LeadSourceViewSet(viewsets.ModelViewSet):
    queryset = LeadSource.objects.all()
    serializer_class = LeadSourceSerializer


class PipelineStageViewSet(viewsets.ModelViewSet):
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by("-created_at")
    filterset_fields = ["stage", "priority", "assigned_to", "source", "is_lost"]
    search_fields = ["name", "company", "mobile", "email", "tags"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LeadDetailSerializer
        return LeadSerializer

    def perform_create(self, serializer):
        # basic duplicate detection by mobile number
        mobile = serializer.validated_data.get("mobile")
        dup = Lead.objects.filter(mobile=mobile).first() if mobile else None
        lead = serializer.save(is_duplicate_of=dup)
        LeadActivity.objects.create(lead=lead, activity_type="CREATED", description="Lead created",
                                     created_by=self.request.user if self.request.user.is_authenticated else None)

    @action(detail=True, methods=["post"])
    def change_stage(self, request, pk=None):
        lead = self.get_object()
        stage_id = request.data.get("stage_id")
        stage = PipelineStage.objects.get(pk=stage_id)
        old_stage = lead.stage.name if lead.stage else ""
        lead.stage = stage
        if stage.is_lost:
            lead.is_lost = True
            lead.lost_reason = request.data.get("lost_reason", lead.lost_reason)
        lead.save()
        LeadActivity.objects.create(lead=lead, activity_type="STAGE_CHANGE",
                                     description=f"Stage changed {old_stage} -> {stage.name}",
                                     created_by=request.user if request.user.is_authenticated else None)
        return Response(LeadSerializer(lead).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        lead = self.get_object()
        lead.is_lost = False
        lead.lost_reason = ""
        lead.save()
        LeadActivity.objects.create(lead=lead, activity_type="REOPENED", description="Lost lead re-opened",
                                     created_by=request.user if request.user.is_authenticated else None)
        return Response(LeadSerializer(lead).data)

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        lead = self.get_object()
        customer = Customer.objects.create(
            name=lead.name, mobile=lead.mobile, email=lead.email,
            salesperson=lead.assigned_to, source=lead.source.name if lead.source else "",
        )
        lead.converted_customer = customer
        lead.save()
        LeadActivity.objects.create(lead=lead, activity_type="CONVERTED",
                                     description=f"Converted to customer #{customer.id}",
                                     created_by=request.user if request.user.is_authenticated else None)
        return Response({"customer_id": customer.id})

    @action(detail=True, methods=["post"])
    def add_note(self, request, pk=None):
        lead = self.get_object()
        note = LeadNote.objects.create(lead=lead, content=request.data.get("content", ""),
                                        author=request.user if request.user.is_authenticated else None)
        return Response(LeadNoteSerializer(note).data)


class FollowUpViewSet(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
    filterset_fields = ["status", "follow_up_type", "assigned_to", "priority", "lead", "customer"]

    @action(detail=False, methods=["get"])
    def today(self, request):
        qs = self.get_queryset().filter(scheduled_at__date=timezone.now().date())
        return Response(FollowUpSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        qs = self.get_queryset().filter(scheduled_at__lt=timezone.now(), status=FollowUp.Status.PENDING)
        return Response(FollowUpSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        qs = self.get_queryset().filter(scheduled_at__gt=timezone.now(), status=FollowUp.Status.PENDING)
        return Response(FollowUpSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        f = self.get_object()
        f.status = FollowUp.Status.COMPLETED
        f.save()
        return Response(FollowUpSerializer(f).data)

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        f = self.get_object()
        f.scheduled_at = request.data.get("scheduled_at", f.scheduled_at)
        f.status = FollowUp.Status.RESCHEDULED
        f.save()
        return Response(FollowUpSerializer(f).data)


class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all().order_by("-created_at")
    serializer_class = QuotationSerializer
    filterset_fields = ["status", "lead", "customer"]
    search_fields = ["quotation_number"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        q = self.get_object()
        q.status = Quotation.Status.SENT
        q.save()
        return Response(QuotationSerializer(q).data)

    @action(detail=True, methods=["post"])
    def revise(self, request, pk=None):
        old = self.get_object()
        new = Quotation.objects.create(
            quotation_number=f"{old.quotation_number}-R{old.version + 1}",
            lead=old.lead, customer=old.customer, status=Quotation.Status.DRAFT,
            terms_and_conditions=old.terms_and_conditions, version=old.version + 1,
            previous_version=old, created_by=request.user if request.user.is_authenticated else None,
        )
        for item in old.items.all():
            QuotationItem.objects.create(
                quotation=new, product=item.product, description=item.description,
                quantity=item.quantity, price=item.price, discount=item.discount, tax_percent=item.tax_percent,
            )
        return Response(QuotationSerializer(new).data)


class QuotationItemViewSet(viewsets.ModelViewSet):
    queryset = QuotationItem.objects.all()
    serializer_class = QuotationItemSerializer
    filterset_fields = ["quotation"]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("due_date")
    serializer_class = TaskSerializer
    filterset_fields = ["status", "priority", "assigned_to", "lead"]

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        task = self.get_object()
        c = TaskComment.objects.create(task=task, content=request.data.get("content", ""),
                                        author=request.user if request.user.is_authenticated else None)
        return Response(TaskCommentSerializer(c).data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        n = self.get_object()
        n.is_read = True
        n.save()
        return Response(NotificationSerializer(n).data)


@api_view(["GET"])
def dashboard_summary(request):
    """Powers the CRM Admin dashboard KPI cards + the Sales CRM dashboard."""
    from vendors.models import Vendor
    from customers.models import Customer as Cust
    from battery.models import Battery
    from coupons.models import Coupon

    won_stage_ids = PipelineStage.objects.filter(is_won=True).values_list("id", flat=True)
    lost_stage_ids = PipelineStage.objects.filter(is_lost=True).values_list("id", flat=True)

    data = {
        "total_vendors": Vendor.objects.count(),
        "pending_vendors": Vendor.objects.filter(status=Vendor.Status.PENDING).count(),
        "approved_vendors": Vendor.objects.filter(status=Vendor.Status.APPROVED).count(),
        "total_customers": Cust.objects.count(),
        "total_batteries": Battery.objects.count(),
        "batteries_in_stock": Battery.objects.filter(status=Battery.Status.IN_STOCK).count(),
        "batteries_sold": Battery.objects.filter(status=Battery.Status.SOLD).count(),
        "active_coupons": Coupon.objects.filter(status=Coupon.Status.ACTIVE).count(),
        "total_leads": Lead.objects.count(),
        "new_leads": Lead.objects.filter(created_at__date=timezone.now().date()).count(),
        "open_deals": Lead.objects.exclude(stage_id__in=list(won_stage_ids) + list(lost_stage_ids)).count(),
        "won_deals": Lead.objects.filter(stage_id__in=won_stage_ids).count(),
        "lost_deals": Lead.objects.filter(is_lost=True).count(),
        "total_pipeline_value": Lead.objects.exclude(stage_id__in=lost_stage_ids).aggregate(v=Sum("expected_deal_value"))["v"] or 0,
        "todays_follow_ups": FollowUp.objects.filter(scheduled_at__date=timezone.now().date()).count(),
        "overdue_follow_ups": FollowUp.objects.filter(scheduled_at__lt=timezone.now(), status=FollowUp.Status.PENDING).count(),
    }
    return Response(data)
