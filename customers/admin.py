from django.contrib import admin
from .models import Customer, CustomerDocument

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "city", "category", "vendor", "salesperson")
    search_fields = ("name", "mobile", "email")

admin.site.register(CustomerDocument)
