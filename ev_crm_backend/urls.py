from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT Authentication
    path(
        "api/auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "api/auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # Accounts
    path("api/", include("accounts.urls")),

    # Vendors
    path("api/", include("vendors.urls")),

    # Products
    path("api/", include("products.urls")),

    # Battery
    path("api/", include("battery.urls")),

    # Customers
    path("api/", include("customers.urls")),

    # Scooters
    path("api/", include("scooters.urls")),

    # Coupons
    path("api/", include("coupons.urls")),

    # CRM
    path("api/", include("crm.urls")),
]


# Serve uploaded product images/media.
#
# Ye DEBUG=False hone par bhi local/server environment me
# /media/... URLs ko serve karega.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]