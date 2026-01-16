# apps/audit/api/urls.py
from django.urls import path
from .views import list_audit_logs

urlpatterns = [
    path('logs/', list_audit_logs, name='audit-logs'),
]