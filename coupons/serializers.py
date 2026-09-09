from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ["created_at", "times_used"]
