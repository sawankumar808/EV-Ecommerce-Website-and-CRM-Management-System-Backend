from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.urls import re_path
from django.views.static import serve

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from accounts.views import current_user
from accounts.authentication import (
    CustomTokenObtainPairSerializer,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from products.views import (
    PublicProductViewSet,
)


class CRMLoginView(
    TokenObtainPairView
):
    serializer_class = (
        CustomTokenObtainPairSerializer
    )


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/auth/login/",
        CRMLoginView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "api/auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    path(
        "api/auth/me/",
        current_user,
        name="current-user",
    ),

    path(
        "api/public-products/",
        PublicProductViewSet.as_view(
            {
                "get": "list"
            }
        ),
        name="public-products-list",
    ), 

    path(
        "api/public-products/<int:pk>/",
        PublicProductViewSet.as_view(
            {
                "get": "retrieve"
            }
        ),
        name="public-product-detail",
    ),

    path(
        "api/accounts/",
        include("accounts.urls")
    ),

    path(
        "api/vendors/",
        include("vendors.urls")
    ),

    path(
        "api/products/",
        include("products.urls")
    ),

    path(
        "api/battery/",
        include("battery.urls")
    ),

    path(
        "api/customers/",
        include("customers.urls")
    ),

    path(
        "api/scooters/",
        include("scooters.urls")
    ),

    path(
        "api/coupons/",
        include("coupons.urls")
    ),

    path(
        "api/crm/",
        include("crm.urls")
    ),
]


urlpatterns += [

    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root":
                settings.MEDIA_ROOT
        },
    ),

]
