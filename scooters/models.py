from django.db import models
from django.conf import settings
from vendors.models import Vendor
from customers.models import Customer


class Scooter(models.Model):
    class Status(models.TextChoices):
        IN_STOCK = "IN_STOCK", "In Stock"
        SOLD = "SOLD", "Sold"
        SERVICE = "SERVICE", "In Service"
        INACTIVE = "INACTIVE", "Inactive"

    scooter_id = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=30, blank=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    chassis_number = models.CharField(max_length=100, unique=True)
    motor_number = models.CharField(max_length=100, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name="scooters")
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL, related_name="scooters")
    purchase_date = models.DateField(null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_STOCK)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.scooter_id


class ScooterBatteryHistory(models.Model):
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, related_name="battery_history")
    battery = models.ForeignKey("battery.Battery", on_delete=models.CASCADE, related_name="scooter_history")
    installed_on = models.DateField()
    removed_on = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True, help_text="Reason for replacement, if applicable")

    class Meta:
        ordering = ["-installed_on"]
        verbose_name_plural = "Scooter battery histories"

    def __str__(self):
        return f"{self.scooter} - {self.battery}"
