import io
import qrcode
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from vendors.models import Vendor


class BatteryBatch(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    batch_number = models.CharField(max_length=50, unique=True)
    battery_model = models.CharField(max_length=100)
    battery_type = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    manufacturing_date = models.DateField()
    added_date = models.DateField(auto_now_add=True)
    g_code = models.CharField(max_length=2, choices=[("G1", "G1"), ("G2", "G2")], blank=True)
    warranty_period_months = models.PositiveIntegerField(default=12)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.CREATED)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.batch_number

    def generate_batteries(self):
        """Generates individual batteries from Battery 001 to N automatically[cite: 3]."""
        batteries_to_create = []
        for i in range(1, self.quantity + 1):
            bat_id = f"Battery {i:03d}"
            serial_no = f"{self.batch_number}-BAT-{i:03d}"
            
            batteries_to_create.append(
                Battery(
                    battery_id=bat_id,
                    serial_number=serial_no,
                    batch=self,
                    model=self.battery_model,
                    battery_type=self.battery_type,
                    g_code=self.g_code,
                    manufacturing_date=self.manufacturing_date,
                    status=Battery.Status.IN_STOCK
                )
            )
        Battery.objects.bulk_create(batteries_to_create)
        self.status = self.Status.COMPLETED
        self.save(update_fields=['status'])


class Battery(models.Model):
    class Status(models.TextChoices):
        ADDED = "ADDED", "Added"
        IN_STOCK = "IN_STOCK", "In Stock"
        ASSIGNED_VENDOR = "ASSIGNED_VENDOR", "Assigned to Vendor"
        SOLD = "SOLD", "Sold"
        ASSIGNED_CUSTOMER = "ASSIGNED_CUSTOMER", "Assigned to Customer"
        INSTALLED = "INSTALLED", "Installed"
        IN_SERVICE = "IN_SERVICE", "In Service"
        RETURNED = "RETURNED", "Returned"
        DAMAGED = "DAMAGED", "Damaged"
        REPLACED = "REPLACED", "Replaced"
        INACTIVE = "INACTIVE", "Inactive"

    battery_id = models.CharField(max_length=50, help_text="e.g. Battery 001")
    serial_number = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey(BatteryBatch, on_delete=models.CASCADE, related_name="batteries")
    model = models.CharField(max_length=100)
    battery_type = models.CharField(max_length=100)
    g_code = models.CharField(max_length=2, choices=[("G1", "G1"), ("G2", "G2")], blank=True)
    manufacturing_date = models.DateField()
    added_date = models.DateField(auto_now_add=True)
    warranty_start = models.DateField(null=True, blank=True)
    warranty_end = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ADDED)

    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL, related_name="batteries")
    customer = models.ForeignKey("customers.Customer", null=True, blank=True, on_delete=models.SET_NULL, related_name="batteries")
    scooter = models.ForeignKey("scooters.Scooter", null=True, blank=True, on_delete=models.SET_NULL, related_name="batteries")
    sales_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    qr_code_image = models.ImageField(upload_to="battery_qr/", blank=True, null=True)
    qr_generated_at = models.DateTimeField(null=True, blank=True)

    def generate_qr_code(self):
        """Generates QR code image containing battery details[cite: 3]."""
        qr_content = f"BATTERY_ID:{self.battery_id}|SERIAL:{self.serial_number}|MODEL:{self.model}|G_CODE:{self.g_code}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        file_name = f"qr_{self.serial_number}.png"
        self.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_image:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.battery_id} ({self.serial_number})"


class BatteryStatusHistory(models.Model):
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, related_name="history")
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    note = models.CharField(max_length=255, blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name_plural = "Battery status histories"

    def __str__(self):
        return f"{self.battery} : {self.from_status} -> {self.to_status}"


# Signal to auto-log status changes in history table
@receiver(pre_save, sender=Battery)
def track_battery_status_change(sender, instance, **kwargs):
    if instance.pk:
        previous = Battery.objects.filter(pk=instance.pk).first()
        if previous and previous.status != instance.status:
            BatteryStatusHistory.objects.create(
                battery=instance,
                from_status=previous.status,
                to_status=instance.status,
                note=f"Status updated to {instance.get_status_display()}"
            )