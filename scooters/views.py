# scooters/views.py

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Scooter, ScooterBatteryHistory
from .serializers import ScooterSerializer, ScooterDetailSerializer

# FIX: 'batteries' ki jagah 'battery' import karein
from battery.models import Battery 


class ScooterViewSet(viewsets.ModelViewSet):
    queryset = Scooter.objects.all().order_by("-created_at")
    filterset_fields = ["status", "vendor", "customer"]
    search_fields = ["scooter_id", "registration_number", "chassis_number"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ScooterDetailSerializer
        return ScooterSerializer

    @action(detail=True, methods=["post"])
    def assign_battery(self, request, pk=None):
        scooter = self.get_object()
        battery_id = request.data.get("battery_id")

        if not battery_id:
            return Response(
                {"error": "battery_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            battery = Battery.objects.get(pk=battery_id)
            
            # Close out active battery on scooter
            ScooterBatteryHistory.objects.filter(
                scooter=scooter, 
                removed_on__isnull=True
            ).update(removed_on=timezone.now().date())

            # Create history entry
            ScooterBatteryHistory.objects.create(
                scooter=scooter, 
                battery=battery, 
                installed_on=timezone.now().date()
            )

            # Update battery status
            battery.scooter = scooter
            battery.status = Battery.Status.INSTALLED
            battery.save()

            return Response(ScooterDetailSerializer(scooter).data, status=status.HTTP_200_OK)

        except Battery.DoesNotExist:
            return Response(
                {"error": f"Battery with ID {battery_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def replace_battery(self, request, pk=None):
        scooter = self.get_object()
        battery_id = request.data.get("battery_id")
        reason = request.data.get("reason", "")

        if not battery_id:
            return Response(
                {"error": "battery_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            old_history = ScooterBatteryHistory.objects.filter(
                scooter=scooter, 
                removed_on__isnull=True
            ).first()

            if old_history:
                old_history.removed_on = timezone.now().date()
                old_history.reason = reason
                old_history.save()

                old_battery = old_history.battery
                old_battery.status = Battery.Status.RETURNED
                old_battery.scooter = None
                old_battery.save()

            new_battery = Battery.objects.get(pk=battery_id)
            ScooterBatteryHistory.objects.create(
                scooter=scooter,
                battery=new_battery,
                installed_on=timezone.now().date(),
                reason=reason
            )

            new_battery.scooter = scooter
            new_battery.status = Battery.Status.INSTALLED
            new_battery.save()

            return Response(ScooterDetailSerializer(scooter).data, status=status.HTTP_200_OK)

        except Battery.DoesNotExist:
            return Response(
                {"error": f"Battery with ID {battery_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )