from rest_framework import serializers
from .models import Product, VendorProductPrice


class VendorProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProductPrice
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """Used for Admin CRM: shows both public and vendor prices."""
    class Meta:
        model = Product
        fields = "__all__"


class ProductPublicSerializer(serializers.ModelSerializer):
    """Used for Public and Vendor portal: automatically switches price based on user role."""
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "model_number", "category", "description", 
            "specifications", "features", "image", "availability", 
            "status", "price", "public_price", "vendor_price"
        ]

    def get_price(self, obj):
        request = self.context.get("request")
        user = request.user if request else None

        # Agar user logged-in Vendor ya Admin hai, toh vendor_price dikhao, warna public_price
        if user and user.is_authenticated and getattr(user, "role", None) in ["VENDOR", "ADMIN"]:
            # Agar vendor-specific override price set hai toh woh do, warna default product vendor_price
            override = VendorProductPrice.objects.filter(product=obj, vendor=getattr(user, "vendor_profile", None)).first()
            if override:
                return override.price
            return obj.vendor_price

        # Public visitor ke liye sirf public_price
        return obj.public_price