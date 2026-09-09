from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Vendor(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"
        INACTIVE = "INACTIVE", "Inactive"

    class BusinessType(models.TextChoices):
        RETAILER = "RETAILER", "Retailer"
        DISTRIBUTOR = "DISTRIBUTOR", "Distributor"
        DEALER = "DEALER", "Dealer"
        SERVICE_CENTER = "SERVICE_CENTER", "Service Center"
        OTHER = "OTHER", "Other"

    business_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    gst_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=15, blank=True)
    business_type = models.CharField(max_length=20, choices=BusinessType.choices, default=BusinessType.RETAILER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    assigned_salesperson = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="vendors"
    )
    login_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="vendor_profile"
    )
    remarks = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class VendorDocument(models.Model):
    class DocType(models.TextChoices):
        GST_CERTIFICATE = "GST_CERTIFICATE", "GST Certificate"
        PAN_CARD = "PAN_CARD", "PAN Card"
        ADDRESS_PROOF = "ADDRESS_PROOF", "Address Proof"
        OTHER = "OTHER", "Other"

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=30, choices=DocType.choices, default=DocType.OTHER)
    file = models.FileField(upload_to="vendor_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.business_name} - {self.get_doc_type_display()}"


class VendorStatusHistory(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.vendor} : {self.from_status} -> {self.to_status}"


class VendorActivity(models.Model):
    """Generic timeline entry used to build the 'Vendor Complete History' view."""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Vendor activities"

    def __str__(self):
        return f"{self.vendor} - {self.activity_type}"

@receiver(post_save, sender=Vendor)
def log_vendor_registration(sender, instance, created, **kwargs):
    if created:
        VendorActivity.objects.create(
            vendor=instance,
            activity_type="REGISTRATION",
            description=f"Vendor registered with initial status: {instance.get_status_display()}"
        )


