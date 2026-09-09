from django.contrib import admin
from .models import Vendor, VendorDocument, VendorStatusHistory, VendorActivity

class VendorDocumentInline(admin.TabularInline):
    model = VendorDocument
    extra = 0

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("business_name", "contact_person", "mobile_number", "city", "status", "assigned_salesperson", "registered_at")
    list_filter = ("status", "business_type", "state")
    search_fields = ("business_name", "contact_person", "mobile_number", "email", "gst_number")
    inlines = [VendorDocumentInline]

admin.site.register(VendorStatusHistory)
admin.site.register(VendorActivity)
