from rest_framework import serializers
from .models import Scooter, ScooterBatteryHistory


class ScooterSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source="customer.name")
    vendor_name = serializers.ReadOnlyField(source="vendor.business_name")
    installed_battery = serializers.SerializerMethodField()

    class Meta:
        model = Scooter
        fields = [
            "id",
            "scooter_id",
            "registration_number",
            "brand",
            "model",
            "chassis_number",
            "motor_number",
            "customer",
            "customer_name",
            "vendor",
            "vendor_name",
            "purchase_date",
            "status",
            "remarks",
            "installed_battery",
            "created_at",
        ]

    def get_installed_battery(self, obj):
        active_history = (
            ScooterBatteryHistory.objects.filter(
                scooter=obj, removed_on__isnull=True
            )
            .select_related("battery")
            .first()
        )

        if active_history and active_history.battery:
            return f"{active_history.battery.battery_id} ({active_history.battery.serial_number})"
        return None


class ScooterDetailSerializer(ScooterSerializer):
    battery_history = serializers.SerializerMethodField()

    class Meta(ScooterSerializer.Meta):
        fields = ScooterSerializer.Meta.fields + ["battery_history"]

    def get_battery_history(self, obj):
        history = ScooterBatteryHistory.objects.filter(scooter=obj).order_by(
            "-installed_on"
        )
        return [
            {
                "id": h.id,
                "battery_id": h.battery.battery_id,
                "serial_number": h.battery.serial_number,
                "installed_on": h.installed_on,
                "removed_on": h.removed_on,
                "reason": h.reason,
            }
            for h in history
        ]