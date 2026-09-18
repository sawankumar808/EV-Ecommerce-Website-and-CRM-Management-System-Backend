from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
)


User = get_user_model()


class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    username = serializers.CharField()

    role = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate(self, attrs):

        identifier = attrs.get(
            "username"
        )

        password = attrs.get(
            "password"
        )

        selected_role = (
            attrs.get("role") or ""
        ).strip().upper()

        user = authenticate(
            request=self.context.get("request"),
            username=identifier,
            password=password,
        )

        if user is None:

            user = (
                User.objects
                .filter(
                    email__iexact=identifier
                )
                .first()
            )

            if (
                user
                and user.check_password(password)
                and user.is_active
            ):
                pass
            else:
                user = None

        if user is None:

            user = (
                User.objects
                .filter(
                    phone=identifier
                )
                .first()
            )

            if (
                user
                and user.check_password(password)
                and user.is_active
            ):
                pass
            else:
                user = None

        if user is None:

            raise AuthenticationFailed(
                "Invalid credentials."
            )

        custom_role = getattr(
            user,
            "custom_role",
            None
        )

        if (
            custom_role
            and custom_role.is_active
        ):
            actual_role = custom_role.code
        else:
            actual_role = user.role

        if (
            selected_role
            and selected_role != actual_role.upper()
        ):
            raise AuthenticationFailed(
                "Invalid credentials."
            )

        data = super().validate(
            {
                "username":
                    user.username,
                "password":
                    password,
            }
        )

        data["user"] = {
            "id": user.id,
            "username": user.username,
            "role": actual_role,
        }

        return data