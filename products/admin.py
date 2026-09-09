from django.contrib import admin
from .models import Product, VendorProductPrice

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "base_price", "status", "availability")
    search_fields = ("name", "sku", "model_number")
    list_filter = ("status", "category")

admin.site.register(VendorProductPrice)
