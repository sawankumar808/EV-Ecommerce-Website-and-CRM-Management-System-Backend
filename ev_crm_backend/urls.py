from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/', include('accounts.urls')),
    path('api/', include('vendors.urls')),
    path('api/', include('products.urls')),
    path('api/', include('battery.urls')),
    path('api/', include('customers.urls')),
    path('api/', include('scooters.urls')),
    path('api/', include('coupons.urls')),
    path('api/', include('crm.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
