from rest_framework.permissions import BasePermission


def user_has_role(user, roles):
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) in roles
    )


class AdminOnly(BasePermission):
    message = "Only CRM Admin can perform this action."

    def has_permission(self, request, view):
        return user_has_role(request.user, ["ADMIN"])


class AdminSales(BasePermission):
    message = "Only CRM Admin or Sales Team can perform this action."

    def has_permission(self, request, view):
        return user_has_role(request.user, ["ADMIN", "SALES"])


class AdminSalesVendor(BasePermission):
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        return user_has_role(request.user, ["ADMIN", "SALES", "VENDOR"])


class VendorOnly(BasePermission):
    message = "Only vendors can access this resource."

    def has_permission(self, request, view):
        return user_has_role(request.user, ["VENDOR"])