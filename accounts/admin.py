from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SalesTarget

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "phone", "is_active_employee")
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role", "phone", "employee_id", "is_active_employee")}),)

admin.site.register(SalesTarget)
