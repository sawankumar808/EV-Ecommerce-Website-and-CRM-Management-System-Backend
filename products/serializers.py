from rest_framework import serializers
from .models import Product, VendorProductPrice


class VendorProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProductPrice
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductPublicSerializer(serializers.ModelSerializer):
    """Used on the public e-commerce listing: price hidden unless an approved vendor is viewing."""
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "model_number", "category", "description", "specifications",
                  "features", "image", "availability", "status", "price"]

    def get_price(self, obj):
        request = self.context.get("request")
        vendor = getattr(request, "approved_vendor", None) if request else None
        if not vendor:
            return None
        override = obj.vendor_prices.filter(vendor=vendor).first()
        return str(override.price if override else obj.base_price)
