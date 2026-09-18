from rest_framework import viewsets, permissions

from .models import Product, VendorProductPrice
from .serializers import (
    ProductSerializer,
    ProductPublicSerializer,
    VendorProductPriceSerializer,
)
from accounts.permissions import AdminOnly, AdminSales


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRM Product Management.

    GET / POST / PUT / PATCH / DELETE:
        Admin / Sales (Allowed for full CRM management)
    """

    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer

    filterset_fields = [
        "status",
        "availability",
        "category",
    ]

    search_fields = [
        "name",
        "sku",
        "model_number",
    ]

    def get_permissions(self):
        # Sabhi actions (list, retrieve, create, update, destroy) ke liye Admin aur Sales dono ko allow kar diya hai
        return [AdminSales()]


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public website product API.

    Kisi user ke login status se koi difference nahi padega.
    Hamesha public_price return hoga.
    """

    queryset = (
        Product.objects
        .filter(status=Product.Status.ACTIVE)
        .order_by("-id")
    )

    serializer_class = ProductPublicSerializer
    permission_classes = [permissions.AllowAny]

    filterset_fields = [
        "category",
        "availability",
    ]

    search_fields = [
        "name",
        "model_number",
    ]


class VendorProductPriceViewSet(viewsets.ModelViewSet):
    """
    Vendor-specific pricing management.

    Sirf Admin vendor price overrides manage kar sakta hai.
    """

    queryset = VendorProductPrice.objects.all()
    serializer_class = VendorProductPriceSerializer
    permission_classes = [AdminOnly]

    filterset_fields = [
        "vendor",
        "product",
    ]    