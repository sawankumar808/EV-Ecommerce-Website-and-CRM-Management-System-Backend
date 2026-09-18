from django.utils import timezone
from django.db.models import Sum

from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from accounts.permissions import AdminSales

from .models import (
    LeadSource,
    PipelineStage,
    Lead,
    LeadNote,
    LeadActivity,
    FollowUp,
    Quotation,
    QuotationItem,
    Task,
    TaskComment,
    Notification,
    Sale,
)

from .serializers import (
    LeadSourceSerializer,
    PipelineStageSerializer,
    LeadSerializer,
    LeadDetailSerializer,
    LeadNoteSerializer,
    FollowUpSerializer,
    QuotationSerializer,
    QuotationItemSerializer,
    TaskSerializer,
    TaskCommentSerializer,
    NotificationSerializer,
    SaleSerializer,
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

    filterset_fields = [
        "stage",
        "priority",
        "assigned_to",
        "source",
        "is_lost",
    ]

    search_fields = [
        "name",
        "company",
        "mobile",
        "email",
        "tags",
    ]

    def get_queryset(self):
        qs = super().get_queryset()

        if getattr(self.request.user, "role", None) == "SALES":
            return qs.filter(
                assigned_to=self.request.user
            )

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LeadDetailSerializer

        return LeadSerializer

    def perform_create(self, serializer):
        mobile = serializer.validated_data.get("mobile")

        duplicate = (
            Lead.objects.filter(mobile=mobile).first()
            if mobile
            else None
        )

        lead = serializer.save(
            is_duplicate_of=duplicate
        )

        LeadActivity.objects.create(
            lead=lead,
            activity_type="CREATED",
            description="Lead created",
            created_by=(
                self.request.user
                if self.request.user.is_authenticated
                else None
            ),
        )

    @action(detail=True, methods=["post"])
    def change_stage(self, request, pk=None):
        lead = self.get_object()

        stage_id = request.data.get("stage_id")

        try:
            stage = PipelineStage.objects.get(
                pk=stage_id
            )
        except PipelineStage.DoesNotExist:
            return Response(
                {"detail": "Pipeline stage not found."},
                status=404,
            )

        old_stage = (
            lead.stage.name
            if lead.stage
            else ""
        )

        lead.stage = stage

        if stage.is_lost:
            lead.is_lost = True
            lead.lost_reason = request.data.get(
                "lost_reason",
                lead.lost_reason
            )

        lead.save()

        LeadActivity.objects.create(
            lead=lead,
            activity_type="STAGE_CHANGE",
            description=(
                f"Stage changed {old_stage} -> {stage.name}"
            ),
            created_by=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        return Response(
            LeadSerializer(lead).data
        )

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        lead = self.get_object()

        lead.is_lost = False
        lead.lost_reason = ""

        lead.save()

        LeadActivity.objects.create(
            lead=lead,
            activity_type="REOPENED",
            description="Lost lead re-opened",
            created_by=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        return Response(
            LeadSerializer(lead).data
        )

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        lead = self.get_object()

        customer = Customer.objects.create(
            name=lead.name,
            mobile=lead.mobile,
            email=lead.email,
            salesperson=lead.assigned_to,
            source=(
                lead.source.name
                if lead.source
                else ""
            ),
        )

        lead.converted_customer = customer
        lead.save()

        LeadActivity.objects.create(
            lead=lead,
            activity_type="CONVERTED",
            description=(
                f"Converted to customer #{customer.id}"
            ),
            created_by=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        return Response(
            {"customer_id": customer.id}
        )

    @action(detail=True, methods=["post"])
    def add_note(self, request, pk=None):
        lead = self.get_object()

        note = LeadNote.objects.create(
            lead=lead,
            content=request.data.get(
                "content",
                ""
            ),
            author=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        return Response(
            LeadNoteSerializer(note).data
        )


class FollowUpViewSet(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer

    filterset_fields = [
        "status",
        "follow_up_type",
        "assigned_to",
        "priority",
        "lead",
        "customer",
    ]

    def get_queryset(self):
        qs = super().get_queryset()

        if getattr(self.request.user, "role", None) == "SALES":
            return qs.filter(
                assigned_to=self.request.user
            )

        return qs

    @action(detail=False, methods=["get"])
    def today(self, request):
        qs = self.get_queryset().filter(
            scheduled_at__date=timezone.now().date()
        )

        return Response(
            FollowUpSerializer(
                qs,
                many=True
            ).data
        )

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        qs = self.get_queryset().filter(
            scheduled_at__lt=timezone.now(),
            status=FollowUp.Status.PENDING,
        )

        return Response(
            FollowUpSerializer(
                qs,
                many=True
            ).data
        )

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        qs = self.get_queryset().filter(
            scheduled_at__gt=timezone.now(),
            status=FollowUp.Status.PENDING,
        )

        return Response(
            FollowUpSerializer(
                qs,
                many=True
            ).data
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        follow_up = self.get_object()

        follow_up.status = FollowUp.Status.COMPLETED
        follow_up.save()

        return Response(
            FollowUpSerializer(
                follow_up
            ).data
        )

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        follow_up = self.get_object()

        follow_up.scheduled_at = request.data.get(
            "scheduled_at",
            follow_up.scheduled_at
        )

        follow_up.status = FollowUp.Status.RESCHEDULED
        follow_up.save()

        return Response(
            FollowUpSerializer(
                follow_up
            ).data
        )


class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all().order_by(
        "-created_at"
    )

    serializer_class = QuotationSerializer

    filterset_fields = [
        "status",
        "lead",
        "customer",
    ]

    search_fields = [
        "quotation_number"
    ]

    def get_queryset(self):
        qs = super().get_queryset()

        if getattr(self.request.user, "role", None) == "SALES":
            return qs.filter(
                created_by=self.request.user
            )

        return qs

    def perform_create(self, serializer):
        serializer.save(
            created_by=(
                self.request.user
                if self.request.user.is_authenticated
                else None
            )
        )

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        quotation = self.get_object()

        quotation.status = Quotation.Status.SENT
        quotation.save()

        return Response(
            QuotationSerializer(
                quotation
            ).data
        )

    @action(detail=True, methods=["post"])
    def revise(self, request, pk=None):
        old = self.get_object()

        new = Quotation.objects.create(
            quotation_number=(
                f"{old.quotation_number}"
                f"-R{old.version + 1}"
            ),
            lead=old.lead,
            customer=old.customer,
            status=Quotation.Status.DRAFT,
            terms_and_conditions=(
                old.terms_and_conditions
            ),
            version=old.version + 1,
            previous_version=old,
            created_by=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        for item in old.items.all():
            QuotationItem.objects.create(
                quotation=new,
                product=item.product,
                description=item.description,
                quantity=item.quantity,
                price=item.price,
                discount=item.discount,
                tax_percent=item.tax_percent,
            )

        return Response(
            QuotationSerializer(new).data
        )


class QuotationItemViewSet(viewsets.ModelViewSet):
    queryset = QuotationItem.objects.all()
    serializer_class = QuotationItemSerializer

    filterset_fields = [
        "quotation"
    ]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by(
        "due_date"
    )

    serializer_class = TaskSerializer

    filterset_fields = [
        "status",
        "priority",
        "assigned_to",
        "lead",
    ]

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        task = self.get_object()

        comment = TaskComment.objects.create(
            task=task,
            content=request.data.get(
                "content",
                ""
            ),
            author=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        return Response(
            TaskCommentSerializer(
                comment
            ).data
        )


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()

        notification.is_read = True
        notification.save()

        return Response(
            NotificationSerializer(
                notification
            ).data
        )


class SaleViewSet(viewsets.ModelViewSet):
    """
    Sales / Orders API.

    ADMIN:
        All sales.

    SALES:
        Only sales created by that salesperson.
    """

    permission_classes = [AdminSales]

    queryset = (
        Sale.objects
        .select_related(
            "vendor",
            "customer",
            "product",
            "created_by",
        )
        .all()
        .order_by("-created_at")
    )

    serializer_class = SaleSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        if getattr(
            self.request.user,
            "role",
            None
        ) == "SALES":
            return qs.filter(
                created_by=self.request.user
            )

        return qs

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


@api_view(["GET"])
def dashboard_summary(request):
    """
    Main CRM dashboard KPI API.

    ADMIN:
        Global CRM totals.

    SALES:
        Salesperson-specific vendors,
        customers, leads, sales and follow-ups.
    """

    from vendors.models import Vendor
    from battery.models import Battery
    from scooters.models import Scooter
    from coupons.models import Coupon

    user = request.user
    is_sales = (
        getattr(user, "role", None)
        == "SALES"
    )

    vendors_qs = Vendor.objects.all()
    customers_qs = Customer.objects.all()
    sales_qs = Sale.objects.all()
    leads_qs = Lead.objects.all()
    followups_qs = FollowUp.objects.all()
    batteries_qs = Battery.objects.all()
    scooters_qs = Scooter.objects.all()
    coupons_qs = Coupon.objects.all()

    if is_sales:
        vendors_qs = vendors_qs.filter(
            assigned_salesperson=user
        )

        customers_qs = customers_qs.filter(
            salesperson=user
        )

        sales_qs = sales_qs.filter(
            created_by=user
        )

        leads_qs = leads_qs.filter(
            assigned_to=user
        )

        followups_qs = followups_qs.filter(
            assigned_to=user
        )

        batteries_qs = batteries_qs.filter(
            sales_person=user
        )

        coupons_qs = coupons_qs.filter(
            created_by=user
        )

    won_stage_ids = PipelineStage.objects.filter(
        is_won=True
    ).values_list(
        "id",
        flat=True
    )

    lost_stage_ids = PipelineStage.objects.filter(
        is_lost=True
    ).values_list(
        "id",
        flat=True
    )

    total_sales_amount = (
        sales_qs.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    pipeline_value = (
        leads_qs
        .exclude(
            stage_id__in=lost_stage_ids
        )
        .aggregate(
            total=Sum("expected_deal_value")
        )["total"]
        or 0
    )

    return Response({

        "total_vendors":
            vendors_qs.count(),

        "pending_vendors":
            vendors_qs.filter(
                status=Vendor.Status.PENDING
            ).count(),

        "approved_vendors":
            vendors_qs.filter(
                status=Vendor.Status.APPROVED
            ).count(),

        "total_customers":
            customers_qs.count(),

        "total_batteries":
            batteries_qs.count(),

        "batteries_in_stock":
            batteries_qs.filter(
                status=Battery.Status.IN_STOCK
            ).count(),

        "batteries_sold":
            batteries_qs.filter(
                status=Battery.Status.SOLD
            ).count(),

        "active_coupons":
            coupons_qs.filter(
                status=Coupon.Status.ACTIVE
            ).count(),

        "total_leads":
            leads_qs.count(),

        "new_leads":
            leads_qs.filter(
                created_at__date=timezone.now().date()
            ).count(),

        "open_deals":
            leads_qs.exclude(
                stage_id__in=list(
                    won_stage_ids
                ) + list(
                    lost_stage_ids
                )
            ).count(),

        "won_deals":
            leads_qs.filter(
                stage_id__in=won_stage_ids
            ).count(),

        "lost_deals":
            leads_qs.filter(
                is_lost=True
            ).count(),

        "total_pipeline_value":
            pipeline_value,

        "todays_follow_ups":
            followups_qs.filter(
                scheduled_at__date=timezone.now().date()
            ).count(),

        "overdue_follow_ups":
            followups_qs.filter(
                scheduled_at__lt=timezone.now(),
                status=FollowUp.Status.PENDING,
            ).count(),

        # Missing earlier — now supplied to Dashboard.
        "total_sales":
            sales_qs.count(),

        "total_sales_amount":
            total_sales_amount,

        # Missing earlier — now supplied to Dashboard.
        "total_scooters":
            scooters_qs.count(),
    })


@api_view(["GET"])
def reports_summary(request):
    """
    Reports page calculations.

    No hard-coded fallback numbers.
    Values are calculated directly from database.
    """

    from vendors.models import Vendor
    from battery.models import Battery
    from scooters.models import Scooter
    from coupons.models import Coupon

    user = request.user
    is_sales = (
        getattr(user, "role", None)
        == "SALES"
    )

    vendors_qs = Vendor.objects.all()
    customers_qs = Customer.objects.all()
    sales_qs = Sale.objects.all()
    batteries_qs = Battery.objects.all()
    scooters_qs = Scooter.objects.all()
    coupons_qs = Coupon.objects.all()

    if is_sales:
        vendors_qs = vendors_qs.filter(
            assigned_salesperson=user
        )

        customers_qs = customers_qs.filter(
            salesperson=user
        )

        sales_qs = sales_qs.filter(
            created_by=user
        )

        batteries_qs = batteries_qs.filter(
            sales_person=user
        )

        coupons_qs = coupons_qs.filter(
            created_by=user
        )

    sales_amount = (
        sales_qs.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    return Response({

        "vendors": {
            "total": vendors_qs.count(),
            "approved": vendors_qs.filter(
                status=Vendor.Status.APPROVED
            ).count(),
            "pending": vendors_qs.filter(
                status=Vendor.Status.PENDING
            ).count(),
        },

        "sales": {
            "total": sales_qs.count(),
            "amount": sales_amount,
        },

        "customers": {
            "total": customers_qs.count(),
        },

        "batteries": {
            "total": batteries_qs.count(),

            "stock":
                batteries_qs.filter(
                    status=Battery.Status.IN_STOCK
                ).count(),

            "sold":
                batteries_qs.filter(
                    status=Battery.Status.SOLD
                ).count(),

            "available":
                batteries_qs.filter(
                    status=Battery.Status.IN_STOCK
                ).count(),

            "assigned":
                batteries_qs.exclude(
                    status=Battery.Status.IN_STOCK
                ).count(),
        },

        "scooters": {
            "total": scooters_qs.count(),
        },

        "coupons": {
            "total": coupons_qs.count(),

            "active":
                coupons_qs.filter(
                    status=Coupon.Status.ACTIVE
                ).count(),

            "used":
                coupons_qs.filter(
                    times_used__gt=0
                ).count(),
        },
    })