from django.contrib import admin
from .models import Product, VendorProductPrice

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'public_price', 'vendor_price', 'status', 'created_at') # 'base_price' ko hata kar 'public_price' kar diya
    search_fields = ('name', 'sku', 'model_number')
    list_filter = ('status', 'category')

@admin.register(VendorProductPrice)
class VendorProductPriceAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'product', 'price')
    list_filter = ('vendor',)