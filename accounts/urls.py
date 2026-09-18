from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    SalesTargetViewSet,
    CustomRoleViewSet,
    current_user,
    public_roles,
    permission_catalog,
    sales_team_summary,
)


router = DefaultRouter()

router.register(
    r"users",
    UserViewSet,
    basename="user"
)

router.register(
    r"sales-targets",
    SalesTargetViewSet,
    basename="salestarget"
)

router.register(
    r"roles",
    CustomRoleViewSet,
    basename="custom-role"
)


urlpatterns = [

    path(
        "me/",
        current_user,
        name="current-user",
    ),

    path(
        "public-roles/",
        public_roles,
        name="public-roles",
    ),

    path(
        "roles/catalog/",
        permission_catalog,
        name="permission-catalog",
    ),

    path(
        "sales-team-summary/",
        sales_team_summary,
        name="sales-team-summary",
    ),

    path(
        "",
        include(router.urls)
    ),
]