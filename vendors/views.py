from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Vendor, VendorDocument, VendorActivity, VendorStatusHistory
from accounts.permissions import AdminOnly, AdminSales, AdminSalesVendor
from .serializers import (
    VendorSerializer, VendorDetailSerializer, VendorDocumentSerializer, VendorRegistrationSerializer,
)


class VendorViewSet(viewsets.ModelViewSet):
    permission_classes=[AdminSales]
    serializer_class = VendorSerializer  # <-- YE MISSING THA, JISSE 500 ERROR AA RAHA THA
    queryset = Vendor.objects.all().order_by("-registered_at")
    filterset_fields = ["status", "business_type", "assigned_salesperson", "city", "state"]
    search_fields = ["business_name", "contact_person", "mobile_number", "email", "gst_number"]
    ordering_fields = ["registered_at", "business_name"]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'history']:
            return VendorDetailSerializer
        return VendorSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Vendor.objects.none()
        
        # 1. ADMIN aur Superuser sabhi vendors dekh sakte hain
        if getattr(user, 'role', '') == 'ADMIN' or user.is_superuser:
            return Vendor.objects.all().order_by("-registered_at")
        
        # 2. SALES User ko sirf unki assigned vendors milenge
        if getattr(user, 'role', '') == 'SALES':
            return Vendor.objects.filter(assigned_salesperson=user).order_by("-registered_at")
            
        # 3. Agar User VENDOR role wala hai, toh sirf apna vendor profile dikhao
        if getattr(user, 'role', '') == 'VENDOR':
            return Vendor.objects.filter(login_user=user).order_by("-registered_at")

        return Vendor.objects.none()

    
    def _change_status(self, request, new_status, note=""):
        if getattr(request.user, "role", None) != "ADMIN" and not request.user.is_superuser:
            return Response({"detail":"Only CRM Admin can change vendor status."}, status=403)
        vendor = self.get_object()
        old_status = vendor.status
        vendor.status = new_status
        vendor.save()
        VendorStatusHistory.objects.create(
            vendor=vendor, from_status=old_status, to_status=new_status,
            changed_by=request.user if request.user.is_authenticated else None, note=note,
        )
        VendorActivity.objects.create(
            vendor=vendor, activity_type="STATUS_CHANGE",
            description=f"Status changed {old_status} -> {new_status}",
        )
        return Response(VendorSerializer(vendor).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._change_status(request, Vendor.Status.APPROVED, request.data.get("note", ""))

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._change_status(request, Vendor.Status.REJECTED, request.data.get("note", ""))

    @action(detail=True, methods=["post"])
    def request_changes(self, request, pk=None):
        return self._change_status(request, Vendor.Status.UNDER_REVIEW, request.data.get("note", ""))

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        return self._change_status(request, Vendor.Status.SUSPENDED, request.data.get("note", ""))

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        return self._change_status(request, Vendor.Status.APPROVED, request.data.get("note", ""))

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        vendor = self.get_object()
        data = VendorDetailSerializer(vendor).data
        return Response(data)


class VendorDocumentViewSet(viewsets.ModelViewSet):
    permission_classes=[AdminOnly]
    queryset = VendorDocument.objects.all()
    serializer_class = VendorDocumentSerializer
    filterset_fields = ["vendor", "doc_type"]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def vendor_register(request):
    """Public endpoint used by the 'Vendor Registration' page on the e-commerce website.
    No login required. Creates the vendor's login account with status PENDING."""
    serializer = VendorRegistrationSerializer(data=request.data)
    serializer.save() if serializer.is_valid(raise_exception=True) else None
    vendor = serializer.instance
    return Response(
        {
            "message": "Registration submitted. You can log in once the CRM Admin approves your account.",
            "vendor_id": vendor.id,
            "status": vendor.status,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def vendor_products(request):
    """Vendor Dashboard 'Available Products' tab: full catalog with this vendor's applicable price."""
    from products.models import Product
    try:
        vendor = Vendor.objects.get(login_user=request.user)
    except Vendor.DoesNotExist:
        return Response({"detail": "No vendor profile linked to this account."}, status=404)
    if vendor.status != Vendor.Status.APPROVED:
        return Response({"detail": "Your account is not yet approved. Prices are hidden until approval."}, status=403)

    products = Product.objects.filter(status=Product.Status.ACTIVE)
    results = []
    for p in products:
        override = p.vendor_prices.filter(vendor=vendor).first()
        results.append({
            "id": p.id, "name": p.name, "model_number": p.model_number, "category": p.category,
            "description": p.description, "image": p.image.url if p.image else None,
            "availability": p.availability,
            "price": str(override.price if override else p.base_price),
        })
    return Response(results)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def vendor_me(request):
    """Used by the Vendor Dashboard after login: returns the logged-in vendor's own profile,
    status and summary stats (orders, batteries, customers, scooters, recent activity)."""
    try:
        vendor = Vendor.objects.get(login_user=request.user)
    except Vendor.DoesNotExist:
        return Response({"detail": "No vendor profile linked to this account."}, status=404)

    from battery.models import Battery
    from customers.models import Customer as Cust
    from scooters.models import Scooter

    data = VendorDetailSerializer(vendor).data
    data["stats"] = {
        "total_batteries": Battery.objects.filter(vendor=vendor).count(),
        "assigned_batteries": Battery.objects.filter(vendor=vendor, status__in=[
            "ASSIGNED_VENDOR", "SOLD", "ASSIGNED_CUSTOMER", "INSTALLED",
        ]).count(),
        "total_customers": Cust.objects.filter(vendor=vendor).count(),
        "total_scooters": Scooter.objects.filter(vendor=vendor).count(),
        "total_orders": __import__("crm.models",fromlist=["Sale"]).Sale.objects.filter(vendor=vendor).count(),
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([AdminSalesVendor])
def vendor_add_customer(request):
    from customers.models import Customer
    from customers.serializers import CustomerSerializer
    vendor=None
    if request.user.role=="VENDOR":
        vendor=Vendor.objects.filter(login_user=request.user).first()
        if not vendor or vendor.status!=Vendor.Status.APPROVED: return Response({"detail":"Vendor is not approved."},status=403)
    else:
        vendor_id=request.data.get("vendor")
        vendor=Vendor.objects.filter(pk=vendor_id).first() if vendor_id else None
    data=request.data.copy(); data["vendor"]=vendor.id if vendor else data.get("vendor"); data["salesperson"]=request.user.id if request.user.role=="SALES" else data.get("salesperson")
    ser=CustomerSerializer(data=data); ser.is_valid(raise_exception=True); obj=ser.save(); return Response(CustomerSerializer(obj).data,status=201)
