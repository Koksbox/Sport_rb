# apps/admin_rb/api/urls.py
from django.urls import path
from .views import list_pending_organizations, assign_role

urlpatterns = [
    path('organizations/pending/', list_pending_organizations, name='admin-pending-orgs'),
    path('roles/assign/', assign_role, name='admin-assign-role'),
]