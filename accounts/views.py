from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import SalesTarget
from .serializers import UserSerializer, UserCreateSerializer, SalesTargetSerializer
from .permissions import AdminOnly, AdminSales

User = get_user_model()


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """Returns the logged-in user's profile + role, used by the frontend to route
    Admin -> CRM dashboard, Sales -> CRM dashboard, Vendor -> Vendor Dashboard."""
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def sales_team_summary(request):
    """Sales Team Management screen: each salesperson with assigned vendor count,
    customer count, coupon count and won/lost deal counts."""
    from vendors.models import Vendor
    from customers.models import Customer
    from coupons.models import Coupon
    from crm.models import Lead

    salespeople = User.objects.filter(role=User.Role.SALES)
    data = []
    for sp in salespeople:
        won = Lead.objects.filter(assigned_to=sp, stage__is_won=True).count()
        lost = Lead.objects.filter(assigned_to=sp, is_lost=True).count()
        total_leads = Lead.objects.filter(assigned_to=sp).count()
        conversion = round((won / total_leads) * 100, 1) if total_leads else 0
        data.append({
            "id": sp.id,
            "name": sp.get_full_name() or sp.username,
            "employee_id": sp.employee_id,
            "mobile": sp.phone,
            "email": sp.email,
            "is_active": sp.is_active_employee,
            "assigned_vendors": Vendor.objects.filter(assigned_salesperson=sp).count(),
            "assigned_customers": Customer.objects.filter(salesperson=sp).count(),
            "coupons_generated": Coupon.objects.filter(created_by=sp).count(),
            "total_leads": total_leads,
            "won_deals": won,
            "lost_deals": lost,
            "conversion_rate": conversion,
        })
    return Response(data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    filterset_fields = ["role", "is_active_employee"]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "employee_id",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create", "update", "partial_update", "destroy"]:
            return [AdminOnly()]

        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        return UserSerializer

class SalesTargetViewSet(viewsets.ModelViewSet):
    queryset = SalesTarget.objects.all()
    serializer_class = SalesTargetSerializer
    filterset_fields = ["salesperson", "month"]

    def get_permissions(self):
        return [AdminSales()]