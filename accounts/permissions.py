from rest_framework.permissions import BasePermission


BUILT_IN_ROLES = {
    "ADMIN",
    "SALES",
    "VENDOR",
}


PERMISSION_CATALOG = [
    {
        "key": "dashboard",
        "label": "Dashboard",
        "actions": ["view"],
    },
    {
        "key": "vendors",
        "label": "Vendors",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "products",
        "label": "Products",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "customers",
        "label": "Customers",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "sales",
        "label": "Sales / Orders",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "sales_team",
        "label": "Sales Team",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "users",
        "label": "Users",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "leads",
        "label": "Sales Pipeline / Leads",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "batteries",
        "label": "Batteries",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "scooters",
        "label": "Scooters",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "coupons",
        "label": "Coupons",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "quotations",
        "label": "Quotations",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "reports",
        "label": "Reports",
        "actions": ["view"],
    },
    {
        "key": "vendor_prices",
        "label": "Vendor Pricing",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "vendor_documents",
        "label": "Vendor Documents",
        "actions": ["view", "add", "edit", "delete"],
    },
    {
        "key": "settings",
        "label": "Site Settings",
        "actions": ["view", "edit"],
    },
]


def user_has_role(user, roles):
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) in roles
    )


def get_custom_role(user):
    if not user or not user.is_authenticated:
        return None

    role = getattr(user, "custom_role", None)

    if role and role.is_active:
        return role

    return None


def is_custom_role_user(user):
    role = get_custom_role(user)

    if role:
        return True

    return (
        getattr(user, "role", None)
        not in BUILT_IN_ROLES
    )


def get_request_resource(request, view=None):

    path = request.path.lower()

    mappings = [
        ("/accounts/roles", "users"),
        ("/accounts/users", "users"),
        ("/accounts/sales-targets", "sales_team"),

        ("/vendors/vendor-documents", "vendor_documents"),
        ("/vendors/vendor/products", "products"),
        ("/vendors/vendor/customers", "customers"),
        ("/vendors/vendor/batteries", "batteries"),
        ("/vendors/vendor/scooters", "scooters"),
        ("/vendors/vendor/orders", "sales"),
        ("/vendors/vendors", "vendors"),

        ("/products/vendor-product-prices", "vendor_prices"),
        ("/products/products", "products"),

        ("/battery/battery-batches", "batteries"),
        ("/battery/batteries", "batteries"),

        ("/customers/customers", "customers"),

        ("/scooters/scooters", "scooters"),

        ("/coupons/coupons", "coupons"),

        ("/crm/leads", "leads"),
        ("/crm/follow-ups", "leads"),
        ("/crm/quotations", "quotations"),
        ("/crm/quotation-items", "quotations"),
        ("/crm/tasks", "sales_team"),
        ("/crm/sales", "sales"),

        ("/crm/dashboard-summary", "dashboard"),
        ("/crm/reports-summary", "reports"),
    ]

    for prefix, resource in mappings:
        if path.startswith(prefix):
            return resource

    if "/dashboard" in path:
        return "dashboard"

    return None


def get_request_action(request, view=None):

    action = getattr(view, "action", None)

    if action in ["list", "retrieve"]:
        return "view"

    if action == "create":
        return "add"

    if action in [
        "update",
        "partial_update",
    ]:
        return "edit"

    if action == "destroy":
        return "delete"

    method = request.method.upper()

    if method == "GET":
        return "view"

    if method == "POST":
        return "add"

    if method in ["PUT", "PATCH"]:
        return "edit"

    if method == "DELETE":
        return "delete"

    return "view"


def custom_role_has_permission(
    user,
    resource,
    action,
):
    role = get_custom_role(user)

    if not role:
        return False

    if not resource:
        return False

    permissions = role.permissions or {}

    allowed = permissions.get(
        resource,
        []
    )

    return action in allowed


class DynamicAccessPermission(BasePermission):

    message = "You do not have permission for this action."

    def has_permission(
        self,
        request,
        view,
    ):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if getattr(user, "role", None) == "ADMIN":
            return True

        if getattr(user, "role", None) == "SALES":
            return True

        resource = get_request_resource(
            request,
            view
        )

        action = get_request_action(
            request,
            view
        )

        return custom_role_has_permission(
            user,
            resource,
            action
        )


class AdminOnly(BasePermission):

    message = "Only CRM Admin or an authorized role can perform this action."

    def has_permission(
        self,
        request,
        view,
    ):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if getattr(user, "role", None) == "ADMIN":
            return True

        resource = get_request_resource(
            request,
            view
        )

        action = get_request_action(
            request,
            view
        )

        return custom_role_has_permission(
            user,
            resource,
            action
        )


class AdminSales(BasePermission):

    message = "You do not have permission for this action."

    def has_permission(
        self,
        request,
        view,
    ):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if getattr(user, "role", None) in [
            "ADMIN",
            "SALES",
        ]:
            return True

        resource = get_request_resource(
            request,
            view
        )

        action = get_request_action(
            request,
            view
        )

        return custom_role_has_permission(
            user,
            resource,
            action
        )


class AdminSalesVendor(BasePermission):

    message = "You do not have permission for this action."

    def has_permission(
        self,
        request,
        view,
    ):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if getattr(user, "role", None) in [
            "ADMIN",
            "SALES",
            "VENDOR",
        ]:
            return True

        resource = get_request_resource(
            request,
            view
        )

        action = get_request_action(
            request,
            view
        )

        return custom_role_has_permission(
            user,
            resource,
            action
        )


class VendorOnly(BasePermission):

    message = "Only vendors can access this resource."

    def has_permission(
        self,
        request,
        view,
    ):
        return user_has_role(
            request.user,
            ["VENDOR"]
        )


class SuperAdminOnly(BasePermission):

    message = "Only CRM Admin can manage roles."

    def has_permission(
        self,
        request,
        view,
    ):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or getattr(
                    request.user,
                    "role",
                    None
                ) == "ADMIN"
            )
        )