from rest_framework import serializers
from .models import (
    LeadSource, PipelineStage, Lead, LeadNote, LeadActivity, FollowUp,
    Quotation, QuotationItem, Task, TaskComment, Notification,
)


class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = "__all__"


class PipelineStageSerializer(serializers.ModelSerializer):
    lead_count = serializers.SerializerMethodField()
    stage_value = serializers.SerializerMethodField()

    class Meta:
        model = PipelineStage
        fields = "__all__"

    def get_lead_count(self, obj):
        return obj.leads.count()

    def get_stage_value(self, obj):
        return sum(l.expected_deal_value for l in obj.leads.all())


class LeadNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = LeadNote
        fields = "__all__"


class LeadActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadActivity
        fields = "__all__"


class LeadSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class LeadDetailSerializer(LeadSerializer):
    notes = LeadNoteSerializer(many=True, read_only=True)
    activities = LeadActivitySerializer(many=True, read_only=True)

    class Meta(LeadSerializer.Meta):
        pass


class FollowUpSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = FollowUp
        fields = "__all__"


class QuotationItemSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = QuotationItem
        fields = "__all__"


class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Quotation
        fields = "__all__"


class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = TaskComment
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    comments = TaskCommentSerializer(many=True, read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)

    class Meta:
        model = Task
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
