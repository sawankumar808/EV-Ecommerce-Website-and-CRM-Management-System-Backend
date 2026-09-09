from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vendor, VendorDocument, VendorStatusHistory, VendorActivity

User = get_user_model()


class VendorDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorDocument
        fields = "__all__"


class VendorStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorStatusHistory
        fields = "__all__"


class VendorActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorActivity
        fields = "__all__"


class VendorSerializer(serializers.ModelSerializer):
    documents = VendorDocumentSerializer(many=True, read_only=True)
    assigned_salesperson_details = serializers.SerializerMethodField()
    assigned_salesperson_name = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = "__all__"
        read_only_fields = ["registered_at", "updated_at"]

    def get_assigned_salesperson_details(self, obj):
        if obj.assigned_salesperson:
            sp = obj.assigned_salesperson
            return {
                "id": sp.id,
                "first_name": sp.first_name,
                "last_name": sp.last_name,
                "username": sp.username,
                "email": getattr(sp, "email", ""),
            }
        return None

    def get_assigned_salesperson_name(self, obj):
        if obj.assigned_salesperson:
            sp = obj.assigned_salesperson
            full_name = f"{sp.first_name} {sp.last_name}".strip()
            return full_name if full_name else sp.username
        return None


class VendorDetailSerializer(VendorSerializer):
    status_history = VendorStatusHistorySerializer(many=True, read_only=True)
    activities = VendorActivitySerializer(many=True, read_only=True)

    class Meta(VendorSerializer.Meta):
        pass


class VendorRegistrationSerializer(serializers.ModelSerializer):
    """Public self-registration used on the E-commerce 'Vendor Registration' page.
    Creates a login User (role=VENDOR) linked to a Vendor with status=PENDING."""

    username = serializers.CharField(write_only=True)
    gst_document = serializers.FileField(write_only=True, required=False)
    pan_document = serializers.FileField(write_only=True, required=False)
    address_document = serializers.FileField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Vendor
        fields = [
            "id", "business_name", "contact_person", "mobile_number", "email",
            "address", "city", "state", "pincode", "gst_number", "pan_number",
            "business_type", "assigned_salesperson", "username", "password", "gst_document", "pan_document", "address_document",
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if Vendor.objects.filter(email=value).exists():
            raise serializers.ValidationError("A vendor with this email has already registered.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        gst_document=validated_data.pop("gst_document",None)
        pan_document=validated_data.pop("pan_document",None)
        address_document=validated_data.pop("address_document",None)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=validated_data.get("email", ""),
            role=User.Role.VENDOR,
        )
        vendor = Vendor.objects.create(
            login_user=user,
            status=Vendor.Status.PENDING,
            **validated_data,
        )
        VendorActivity.objects.create(
            vendor=vendor, activity_type="REGISTERED", description="Vendor self-registered on the website",
        )
        VendorStatusHistory.objects.create(vendor=vendor, from_status="", to_status=Vendor.Status.PENDING)
        for doc_type, file_obj in [(VendorDocument.DocType.GST_CERTIFICATE,gst_document),(VendorDocument.DocType.PAN_CARD,pan_document),(VendorDocument.DocType.ADDRESS_PROOF,address_document)]:
            if file_obj: VendorDocument.objects.create(vendor=vendor, doc_type=doc_type, file=file_obj)
        return vendor