from django.db import models
from vendors.models import Vendor
from django.conf import settings


class Customer(models.Model):
    class Category(models.TextChoices):
        RETAIL = "RETAIL", "Retail"
        FLEET = "FLEET", "Fleet"
        CORPORATE = "CORPORATE", "Corporate"

    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    category = models.CharField(max_length=15, choices=Category.choices, default=Category.RETAIL)
    source = models.CharField(max_length=100, blank=True)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL, related_name="customers")
    salesperson = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="customers")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomerDocument(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="customer_documents/")
    label = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
