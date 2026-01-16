# apps/core/api/urls.py
from django.urls import path
from .views import list_consents, update_consent, system_constants, health_check

urlpatterns = [
    path('consents/', list_consents, name='core-consents'),
    path('consents/update/', update_consent, name='core-update-consent'),
    path('constants/', system_constants, name='core-constants'),
    path('health/', health_check, name='core-health'),
]