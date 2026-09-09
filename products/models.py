from django.db import models
from vendors.models import Vendor


class Product(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    name = models.CharField(max_length=255)
    model_number = models.CharField(max_length=100, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    specifications = models.JSONField(default=dict, blank=True, help_text="Key/value spec pairs")
    features = models.TextField(blank=True, help_text="One feature per line")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Hidden from visitors; visible to approved vendors")
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class VendorProductPrice(models.Model):
    """Vendor-specific pricing override."""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="product_prices")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="vendor_prices")
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("vendor", "product")

    def __str__(self):
        return f"{self.vendor} - {self.product}: {self.price}"
