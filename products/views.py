from rest_framework import viewsets, permissions
from .models import Product, VendorProductPrice
from .serializers import ProductSerializer, ProductPublicSerializer, VendorProductPriceSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    filterset_fields = ["status", "availability", "category"]
    search_fields = ["name", "sku", "model_number"]


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    """No auth required: powers the public e-commerce product listing. Price is None unless
    an approved vendor session is attached to the request (see auth middleware / frontend token)."""
    queryset = Product.objects.filter(status=Product.Status.ACTIVE)
    serializer_class = ProductPublicSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["category", "availability"]
    search_fields = ["name", "model_number"]


class VendorProductPriceViewSet(viewsets.ModelViewSet):
    queryset = VendorProductPrice.objects.all()
    serializer_class = VendorProductPriceSerializer
    filterset_fields = ["vendor", "product"]
