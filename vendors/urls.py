from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, VendorDocumentViewSet, vendor_register, vendor_me, vendor_products, vendor_add_customer

router = DefaultRouter()
router.register("vendors", VendorViewSet)
router.register("vendor-documents", VendorDocumentViewSet)

urlpatterns = router.urls + [
    path("vendor/register/", vendor_register, name="vendor-register"),
    path("vendor/me/", vendor_me, name="vendor-me"),
    path("vendor/products/", vendor_products, name="vendor-products"),
    path("vendor/customers/", vendor_add_customer, name="vendor-add-customer"),
]
