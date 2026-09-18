import random
import re

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import SalesTarget, CustomRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "role_name",
            "permissions",
            "employee_id",
            "is_active_employee",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "permissions",
        ]

    def get_role_name(self, obj):
        if obj.role == "ADMIN":
            return "CRM Admin"
        if obj.role == "SALES":
            return "Sales Executive"
        if obj.role == "VENDOR":
            return "Vendor Partner"

        role = CustomRole.objects.filter(
            code=obj.role,
            is_active=True
        ).first()

        return role.name if role else obj.role

    def get_permissions(self, obj):
        permissions = {}
        try:
            if obj.role in ["ADMIN", "SALES"] or obj.is_superuser:
                return {"all": ["view", "add", "change", "delete"]}
            
            role_obj = CustomRole.objects.filter(code=obj.role, is_active=True).first()
            if role_obj and role_obj.permissions:
                return role_obj.permissions
        except Exception as e:
            print("Error processing permissions:", e)
        
        return permissions


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    employee_id = serializers.CharField(
        required=False,
        allow_blank=True
    )

    phone = serializers.CharField(
        required=False,
        allow_blank=True
    )

    # Frontend se custom_role ID aayegi, use handle karne ke liye field add ki hai
    custom_role = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "custom_role",
            "employee_id",
            "password",
        ]

    def validate_role(self, value):
        value = value.strip().upper()

        if value in ["ADMIN", "SALES", "VENDOR"]:
            return value

        if not CustomRole.objects.filter(
            code=value,
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "Selected role does not exist."
            )

        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )
        return value

    def validate_email(self, value):
        if value and User.objects.filter(
            email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        custom_role_id = validated_data.pop("custom_role", None)

        # Agar frontend se custom_role ID aayi hai, toh uska code fetch karke user ke role mein set kar do
        if custom_role_id:
            try:
                role_obj = CustomRole.objects.get(id=custom_role_id)
                validated_data["role"] = role_obj.code
            except CustomRole.DoesNotExist:
                pass

        if not validated_data.get("employee_id"):
            validated_data["employee_id"] = (
                f"EMP-{random.randint(1000, 999999)}"
            )

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        custom_role_id = validated_data.pop("custom_role", None)

        if custom_role_id is not None:
            if custom_role_id:
                try:
                    role_obj = CustomRole.objects.get(id=custom_role_id)
                    instance.role = role_obj.code
                except CustomRole.DoesNotExist:
                    pass
            else:
                instance.role = "SALES"

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class CustomRoleSerializer(serializers.ModelSerializer):
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomRole
        fields = [
            "id",
            "name",
            "code",
            "category",
            "permissions",
            "is_active",
            "users_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "users_count",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Role name is required."
            )
        return value

    def create(self, validated_data):
        name = validated_data["name"]

        code = re.sub(
            r"[^A-Z0-9_]+",
            "_",
            name.upper()
        ).strip("_")

        if not code:
            raise serializers.ValidationError(
                {"name": "Invalid role name."}
            )

        original = code
        counter = 2

        while CustomRole.objects.filter(code=code).exists():
            code = f"{original}_{counter}"
            counter += 1

        validated_data["code"] = code
        return super().create(validated_data)

    def get_users_count(self, obj):
        return User.objects.filter(
            role=obj.code
        ).count()


class SalesTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTarget
        fields = "__all__"