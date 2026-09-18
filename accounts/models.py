from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomRole(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    permissions = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Super Admin / CRM Admin"
        SALES = "SALES", "Sales Team"
        VENDOR = "VENDOR", "Vendor"

    role = models.CharField(max_length=50, default="SALES")
    phone = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=30, blank=True, null=True, unique=True)
    is_active_employee = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class SalesTarget(models.Model):
    salesperson = models.ForeignKey(User, on_delete=models.CASCADE, related_name="targets")
    month = models.DateField(help_text="Use the first day of the target month")
    target_amount = models.DecimalField(max_digits=14, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        unique_together = ("salesperson", "month")

    def __str__(self):
        return f"{self.salesperson} - {self.month:%b %Y}"