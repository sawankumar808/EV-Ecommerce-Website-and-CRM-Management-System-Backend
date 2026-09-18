from rest_framework import viewsets, permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import (
    SalesTarget,
    CustomRole,
)

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    SalesTargetSerializer,
    CustomRoleSerializer,
)

from .permissions import (
    AdminOnly,
    AdminSales,
    SuperAdminOnly,
    PERMISSION_CATALOG,
)


User = get_user_model()


@api_view(["GET"])
@permission_classes([
    permissions.IsAuthenticated
])
def current_user(request):

    return Response(
        UserSerializer(
            request.user
        ).data
    )


@api_view(["GET"])
@permission_classes([
    permissions.AllowAny
])
def public_roles(request):

    data = [
        {
            "value": "ADMIN",
            "label": "CRM Admin",
            "type": "builtin",
        },
        {
            "value": "SALES",
            "label": "Sales Executive",
            "type": "builtin",
        },
        {
            "value": "VENDOR",
            "label": "Vendor Partner",
            "type": "builtin",
        },
    ]

    custom_roles = (
        CustomRole.objects
        .filter(is_active=True)
        .order_by("name")
    )

    for role in custom_roles:

        data.append(
            {
                "value": role.code,
                "label": role.name,
                "type": "custom",
                "category": role.category,
            }
        )

    return Response(data)


@api_view(["GET"])
@permission_classes([
    permissions.IsAuthenticated
])
def permission_catalog(request):

    return Response(
        PERMISSION_CATALOG
    )


@api_view(["GET"])
@permission_classes([
    permissions.IsAuthenticated
])
def sales_team_summary(request):

    from vendors.models import Vendor
    from customers.models import Customer
    from coupons.models import Coupon
    from crm.models import Lead

    salespeople = User.objects.filter(
        role=User.Role.SALES
    )

    data = []

    for sp in salespeople:

        won = Lead.objects.filter(
            assigned_to=sp,
            stage__is_won=True
        ).count()

        lost = Lead.objects.filter(
            assigned_to=sp,
            is_lost=True
        ).count()

        total_leads = Lead.objects.filter(
            assigned_to=sp
        ).count()

        conversion = (
            round(
                (won / total_leads) * 100,
                1
            )
            if total_leads
            else 0
        )

        data.append(
            {
                "id": sp.id,
                "name":
                    sp.get_full_name()
                    or sp.username,

                "employee_id":
                    sp.employee_id,

                "mobile":
                    sp.phone,

                "email":
                    sp.email,

                "is_active":
                    sp.is_active_employee,

                "assigned_vendors":
                    Vendor.objects.filter(
                        assigned_salesperson=sp
                    ).count(),

                "assigned_customers":
                    Customer.objects.filter(
                        salesperson=sp
                    ).count(),

                "coupons_generated":
                    Coupon.objects.filter(
                        created_by=sp
                    ).count(),

                "total_leads":
                    total_leads,

                "won_deals":
                    won,

                "lost_deals":
                    lost,

                "conversion_rate":
                    conversion,
            }
        )

    return Response(data)


class UserViewSet(
    viewsets.ModelViewSet
):

    queryset = User.objects.all().order_by(
        "-created_at"
    )

    filterset_fields = [
        "role",
        "is_active_employee",
        # "custom_role",  # Removed to fix 500 error
    ]

    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
        "employee_id",
    ]

    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                AdminOnly()
            ]

        return [
            permissions.IsAuthenticated()
        ]

    def get_serializer_class(self):

        if self.action == "create":
            return UserCreateSerializer

        return UserSerializer


class CustomRoleViewSet(
    viewsets.ModelViewSet
):

    queryset = CustomRole.objects.all().order_by(
        "name"
    )

    serializer_class = CustomRoleSerializer

    permission_classes = [
        SuperAdminOnly
    ]

    def perform_destroy(self, instance):

        User.objects.filter(
            custom_role=instance
        ).update(
            role="SALES",
            custom_role=None,
        )

        instance.delete()


class SalesTargetViewSet(
    viewsets.ModelViewSet
):

    queryset = SalesTarget.objects.all()

    serializer_class = SalesTargetSerializer

    filterset_fields = [
        "salesperson",
        "month",
    ]

    def get_permissions(self):

        return [
            AdminSales()
        ]