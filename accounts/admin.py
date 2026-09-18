# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomRole

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Roles', {'fields': ('role', 'custom_role', 'phone')}),
    )

@admin.register(CustomRole)
class CustomRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')