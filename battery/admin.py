from django.contrib import admin
from .models import BatteryBatch, Battery, BatteryStatusHistory

@admin.register(BatteryBatch)
class BatteryBatchAdmin(admin.ModelAdmin):
    list_display = ("batch_number", "battery_model", "quantity", "g_code", "status", "added_date")
    search_fields = ("batch_number", "battery_model")

@admin.register(Battery)
class BatteryAdmin(admin.ModelAdmin):
    list_display = ("battery_id", "serial_number", "batch", "status", "vendor", "customer", "scooter")
    list_filter = ("status", "g_code")
    search_fields = ("battery_id", "serial_number")

admin.site.register(BatteryStatusHistory)
