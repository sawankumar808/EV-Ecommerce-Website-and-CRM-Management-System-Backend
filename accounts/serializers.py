import random
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SalesTarget



User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone",
                  "role", "employee_id", "is_active_employee", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    employee_id = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone",
                  "role", "employee_id", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        
        # Auto-generate Employee ID if not provided
        if not validated_data.get("employee_id"):
            validated_data["employee_id"] = f"EMP-{random.randint(1000, 9999)}"
            
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SalesTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTarget
        fields = "__all__"