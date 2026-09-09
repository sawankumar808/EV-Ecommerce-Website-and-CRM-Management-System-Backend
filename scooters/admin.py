from django.contrib import admin
from .models import Scooter, ScooterBatteryHistory

@admin.register(Scooter)
class ScooterAdmin(admin.ModelAdmin):
    list_display = ("scooter_id", "registration_number", "brand", "model", "customer", "vendor", "status")
    search_fields = ("scooter_id", "registration_number", "chassis_number")

admin.site.register(ScooterBatteryHistory)
