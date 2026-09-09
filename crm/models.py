from django.db import models
from django.conf import settings
from customers.models import Customer
from products.models import Product


class LeadSource(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class PipelineStage(models.Model):
    """Custom, orderable sales stages: New Lead, Contacted, Qualified, Proposal, Negotiation, Won, Lost..."""
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Lead(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    name = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    source = models.ForeignKey(LeadSource, null=True, blank=True, on_delete=models.SET_NULL, related_name="leads")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="leads")
    stage = models.ForeignKey(PipelineStage, on_delete=models.PROTECT, related_name="leads")
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    score = models.PositiveIntegerField(default=0)
    expected_deal_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    probability_percent = models.PositiveIntegerField(default=10)
    expected_closing_date = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma separated tags")
    is_duplicate_of = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="duplicates")
    lost_reason = models.CharField(max_length=255, blank=True)
    is_lost = models.BooleanField(default=False)
    converted_customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name="leads")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class LeadActivity(models.Model):
    """Timeline entries: created, stage change, assignment, note added, converted, reopened, etc."""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Lead activities"


class FollowUp(models.Model):
    class Type(models.TextChoices):
        CALL = "CALL", "Call"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        EMAIL = "EMAIL", "Email"
        MEETING = "MEETING", "Meeting"
        DEMO = "DEMO", "Demo"
        SITE_VISIT = "SITE_VISIT", "Site Visit"
        OTHER = "OTHER", "Other"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        MISSED = "MISSED", "Missed"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"

    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.CASCADE, related_name="follow_ups")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE, related_name="follow_ups")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follow_ups")
    follow_up_type = models.CharField(max_length=15, choices=Type.choices, default=Type.CALL)
    scheduled_at = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_days = models.PositiveIntegerField(null=True, blank=True)
    next_follow_up = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="previous")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"{self.get_follow_up_type_display()} - {self.scheduled_at:%Y-%m-%d %H:%M}"


class Quotation(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SENT = "SENT", "Sent"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    quotation_number = models.CharField(max_length=50, unique=True)
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL, related_name="quotations")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name="quotations")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    terms_and_conditions = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="revisions")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return sum(item.total for item in self.items.all())

    def __str__(self):
        return self.quotation_number


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def total(self):
        subtotal = (self.price * self.quantity) - self.discount
        return subtotal + (subtotal * self.tax_percent / 100)


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    content = models.TextField()
    attachment = models.FileField(upload_to="task_attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Sale(models.Model):
    sale_number = models.CharField(max_length=50, unique=True)
    # VENDOR FIELD ADD KIYA:
    vendor = models.ForeignKey('vendors.Vendor', null=True, blank=True, on_delete=models.SET_NULL, related_name="sales")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name="sales")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="sales")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default="COMPLETED")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sale_number} - {self.amount}"
