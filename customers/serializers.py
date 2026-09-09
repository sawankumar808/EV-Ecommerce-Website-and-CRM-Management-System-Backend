from rest_framework import serializers
from .models import Customer, CustomerDocument


class CustomerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDocument
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    documents = CustomerDocumentSerializer(many=True, read_only=True)
    vendor_name = serializers.CharField(source="vendor.business_name", read_only=True)
    salesperson_name = serializers.CharField(source="salesperson.get_full_name", read_only=True)

    class Meta:
        model = Customer
        fields = "__all__"
