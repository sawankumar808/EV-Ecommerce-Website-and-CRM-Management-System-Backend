from django.contrib import admin
from .models import (LeadSource, PipelineStage, Lead, LeadNote, LeadActivity, FollowUp,
                      Quotation, QuotationItem, Task, TaskComment, Notification)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "mobile", "stage", "priority", "assigned_to", "expected_deal_value")
    list_filter = ("stage", "priority", "is_lost")
    search_fields = ("name", "company", "mobile", "email")

@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_won", "is_lost")

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ("lead", "customer", "follow_up_type", "scheduled_at", "status", "assigned_to")
    list_filter = ("status", "follow_up_type")

admin.site.register(LeadSource)
admin.site.register(LeadNote)
admin.site.register(LeadActivity)
admin.site.register(Quotation)
admin.site.register(QuotationItem)
admin.site.register(Task)
admin.site.register(TaskComment)
admin.site.register(Notification)
