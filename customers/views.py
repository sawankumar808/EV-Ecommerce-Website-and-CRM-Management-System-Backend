from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer, CustomerDocument
from .serializers import CustomerSerializer, CustomerDocumentSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer
    filterset_fields = ["category", "vendor", "salesperson", "city"]
    search_fields = ["name", "mobile", "email"]

    @action(detail=True, methods=["get"])
    def full_history(self, request, pk=None):
        """Customer detail page: purchased products, battery info, scooter info,
        vendor, salesperson, purchase history and battery history all in one call."""
        from battery.models import Battery
        from scooters.models import Scooter
        from crm.models import Quotation

        customer = self.get_object()
        batteries = Battery.objects.filter(customer=customer)
        scooters = Scooter.objects.filter(customer=customer)
        quotations = Quotation.objects.filter(customer=customer)

        return Response({
            "customer": CustomerSerializer(customer).data,
            "batteries": [{
                "id": b.id, "battery_id": b.battery_id, "model": b.model, "serial_number": b.serial_number,
                "batch_number": b.batch.batch_number, "g_code": b.g_code, "status": b.status,
                "warranty_start": b.warranty_start, "warranty_end": b.warranty_end,
            } for b in batteries],
            "scooters": [{
                "id": s.id, "scooter_id": s.scooter_id, "registration_number": s.registration_number,
                "brand": s.brand, "model": s.model, "status": s.status,
            } for s in scooters],
            "quotations": [{
                "id": q.id, "quotation_number": q.quotation_number, "status": q.status,
                "total_amount": str(q.total_amount), "created_at": q.created_at,
            } for q in quotations],
        })


class CustomerDocumentViewSet(viewsets.ModelViewSet):
    queryset = CustomerDocument.objects.all()
    serializer_class = CustomerDocumentSerializer
    filterset_fields = ["customer"]
