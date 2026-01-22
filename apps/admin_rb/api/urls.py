# apps/admin_rb/api/urls.py
from django.urls import path
from .views import (
    get_dashboard_stats, list_pending_organizations, assign_role,
    get_system_logs, get_users_list, toggle_user_status, get_organizations_list
)

urlpatterns = [
    path('stats/', get_dashboard_stats, name='admin-dashboard-stats'),
    path('organizations/pending/', list_pending_organizations, name='admin-pending-orgs'),
    path('organizations/', get_organizations_list, name='admin-organizations-list'),
    path('roles/assign/', assign_role, name='admin-assign-role'),
    path('logs/', get_system_logs, name='admin-system-logs'),
    path('users/', get_users_list, name='admin-users-list'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='admin-toggle-user-status'),
]