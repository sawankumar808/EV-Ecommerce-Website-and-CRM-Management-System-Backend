from django.db import models
from django.conf import settings
from vendors.models import Vendor
from customers.models import Customer


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "PERCENTAGE", "Percentage"
        FIXED = "FIXED", "Fixed Amount"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        USED = "USED", "Used"
        EXPIRED = "EXPIRED", "Expired"
        DISABLED = "DISABLED", "Disabled"

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=15, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_purchase = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL, related_name="coupons")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name="coupons")
    usage_limit = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="coupons_created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
