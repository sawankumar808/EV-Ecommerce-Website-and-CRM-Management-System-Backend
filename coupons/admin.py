from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "status", "expiry_date", "created_by")
    search_fields = ("code",)
    list_filter = ("status", "discount_type")
