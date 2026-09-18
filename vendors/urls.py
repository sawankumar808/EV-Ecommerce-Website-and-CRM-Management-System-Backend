from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    VendorViewSet,
    VendorDocumentViewSet,
    vendor_register,
    vendor_me,
    vendor_products,
    vendor_customers,
    vendor_customer_detail,
    vendor_batteries,
    vendor_scooters,
    vendor_order,
)


router = DefaultRouter()

router.register(
    "vendors",
    VendorViewSet,
    basename="vendors"
)

router.register(
    "vendor-documents",
    VendorDocumentViewSet,
    basename="vendor-documents"
)


urlpatterns = router.urls + [

    path(
        "vendor/register/",
        vendor_register,
        name="vendor-register",
    ),

    path(
        "vendor/me/",
        vendor_me,
        name="vendor-me",
    ),

    path(
        "vendor/products/",
        vendor_products,
        name="vendor-products",
    ),

    path(
        "vendor/customers/",
        vendor_customers,
        name="vendor-customers",
    ),

    path(
        "vendor/customers/<int:pk>/",
        vendor_customer_detail,
        name="vendor-customer-detail",
    ),

    path(
        "vendor/batteries/",
        vendor_batteries,
        name="vendor-batteries",
    ),

    path(
        "vendor/scooters/",
        vendor_scooters,
        name="vendor-scooters",
    ),

    path(
        "vendor/orders/",
        vendor_order,
        name="vendor-order",
    ),
]