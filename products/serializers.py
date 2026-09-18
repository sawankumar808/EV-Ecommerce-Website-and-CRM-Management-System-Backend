from rest_framework import serializers
from .models import Product, VendorProductPrice


class VendorProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProductPrice
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """
    CRM Product Management.

    Admin/Sales CRM me public_price aur vendor_price
    dono visible rahenge.
    """

    class Meta:
        model = Product
        fields = "__all__"


class ProductPublicSerializer(serializers.ModelSerializer):
    """
    PUBLIC WEBSITE PRODUCT SERIALIZER.

    Important:
    Visitor ko hamesha public_price milega.

    Even if ADMIN/VENDOR login hai aur public website open
    karta hai, yahan vendor price nahi jayega.

    Vendor-specific pricing ke liye separate
    /vendor/products/ endpoint use hota hai.
    """

    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "model_number",
            "sku",
            "category",
            "description",
            "specifications",
            "features",
            "image",
            "availability",
            "status",
            "price",
            "public_price",
        ]

    def get_price(self, obj):
        # PUBLIC PAGE = PUBLIC PRICE ONLY
        return obj.public_price