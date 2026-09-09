from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from accounts.permissions import AdminOnly, AdminSales
from .models import BatteryBatch, Battery, BatteryStatusHistory
from .serializers import BatteryBatchSerializer, BatterySerializer, BatteryDetailSerializer, BatteryStatusHistorySerializer

class BatteryBatchViewSet(viewsets.ModelViewSet):
    queryset=BatteryBatch.objects.all().order_by("-added_date")
    serializer_class=BatteryBatchSerializer
    permission_classes=[AdminOnly]
    filterset_fields=["status","battery_model","battery_type","g_code"]
    search_fields=["batch_number","battery_model","battery_type"]
    def perform_create(self, serializer): serializer.save(created_by=self.request.user)
    @action(detail=True, methods=["post"])
    def generate_batteries(self, request, pk=None):
        batch=self.get_object(); existing=batch.batteries.count()
        if existing>=batch.quantity: return Response({"detail":"All batteries already generated.","generated":existing})
        for i in range(existing+1,batch.quantity+1):
            Battery.objects.create(battery_id=f"{batch.batch_number}-BAT-{i:03d}",serial_number=f"{batch.batch_number}-SER-{i:04d}",batch=batch,model=batch.battery_model,battery_type=batch.battery_type,g_code=batch.g_code,manufacturing_date=batch.manufacturing_date,status=Battery.Status.IN_STOCK,warranty_start=batch.manufacturing_date,warranty_end=batch.manufacturing_date.replace(year=batch.manufacturing_date.year + max(1,batch.warranty_period_months//12)))
        batch.status=BatteryBatch.Status.COMPLETED; batch.save(update_fields=["status"]); return Response(BatteryBatchSerializer(batch).data)

class BatteryViewSet(viewsets.ModelViewSet):
    queryset=Battery.objects.select_related("batch","vendor","customer","scooter").all().order_by("-added_date")
    serializer_class=BatterySerializer
    permission_classes=[AdminOnly]
    filterset_fields=["status","batch","g_code","vendor","customer","scooter"]
    search_fields=["battery_id","serial_number","batch__batch_number","model"]
    def get_serializer_class(self): return BatteryDetailSerializer if self.action=="retrieve" else BatterySerializer
    @action(detail=True, methods=["post"])
    def status(self, request, pk=None):
        b=self.get_object(); new=request.data.get("status")
        valid=dict(Battery.Status.choices)
        if new not in valid: return Response({"detail":"Invalid battery status."},status=400)
        old=b.status; b.status=new; b.save(update_fields=["status"])
        BatteryStatusHistory.objects.create(battery=b,from_status=old,to_status=new,changed_by=request.user,note=request.data.get("note",""))
        return Response(BatteryDetailSerializer(b).data)
    @action(detail=True, methods=["post"])
    def assign_vendor(self, request, pk=None):
        from vendors.models import Vendor
        b=self.get_object()
        try: vendor=Vendor.objects.get(pk=request.data.get("vendor"))
        except Vendor.DoesNotExist: return Response({"detail":"Vendor not found"},status=404)
        old=b.status; b.vendor=vendor; b.status=Battery.Status.ASSIGNED_VENDOR; b.sales_person=request.user; b.save()
        BatteryStatusHistory.objects.create(battery=b,from_status=old,to_status=b.status,changed_by=request.user,note=f"Assigned to {vendor.business_name}")
        return Response(BatteryDetailSerializer(b).data)
    @action(detail=True, methods=["post"])
    def assign_customer(self, request, pk=None):
        from customers.models import Customer
        b=self.get_object()
        try: customer=Customer.objects.get(pk=request.data.get("customer"))
        except Customer.DoesNotExist: return Response({"detail":"Customer not found"},status=404)
        old=b.status; b.customer=customer; b.status=Battery.Status.ASSIGNED_CUSTOMER; b.save()
        BatteryStatusHistory.objects.create(battery=b,from_status=old,to_status=b.status,changed_by=request.user,note=f"Assigned to {customer.name}")
        return Response(BatteryDetailSerializer(b).data)
    @action(detail=True, methods=["post"])
    def assign_scooter(self, request, pk=None):
        from scooters.models import Scooter
        b=self.get_object()
        try: scooter=Scooter.objects.get(pk=request.data.get("scooter"))
        except Scooter.DoesNotExist: return Response({"detail":"Scooter not found"},status=404)
        old=b.status; b.scooter=scooter; b.customer=scooter.customer; b.vendor=scooter.vendor; b.status=Battery.Status.INSTALLED; b.save()
        return Response(BatteryDetailSerializer(b).data)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
@api_view(["GET"])
@permission_classes([AllowAny])
def public_battery(request, serial):
    try: b=Battery.objects.select_related("batch","vendor","customer","scooter").get(serial_number=serial)
    except Battery.DoesNotExist: return Response({"detail":"Battery not found"},status=404)
    return Response({"battery_id":b.battery_id,"serial_number":b.serial_number,"model":b.model,"battery_type":b.battery_type,"g_code":b.g_code,"batch":b.batch.batch_number,"manufacturing_date":b.manufacturing_date,"warranty_start":b.warranty_start,"warranty_end":b.warranty_end,"status":b.status,"vendor":b.vendor.business_name if b.vendor else None,"customer":b.customer.name if b.customer else None,"scooter":b.scooter.scooter_id if b.scooter else None})
