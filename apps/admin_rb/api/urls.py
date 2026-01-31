# apps/admin_rb/api/urls.py
from django.urls import path
from .views import (
    get_dashboard_stats, list_pending_organizations, assign_role,
    get_system_logs, get_users_list, toggle_user_status, get_organizations_list,
    create_notification, news_articles_list, news_article_detail,
    generate_committee_code, list_committee_codes, delete_committee_code,
    archive_committee_code, restore_committee_code
)

urlpatterns = [
    path('stats/', get_dashboard_stats, name='admin-dashboard-stats'),
    path('organizations/pending/', list_pending_organizations, name='admin-pending-orgs'),
    path('organizations/', get_organizations_list, name='admin-organizations-list'),
    path('roles/assign/', assign_role, name='admin-assign-role'),
    path('logs/', get_system_logs, name='admin-system-logs'),
    path('users/', get_users_list, name='admin-users-list'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='admin-toggle-user-status'),
    path('notifications/create/', create_notification, name='admin-create-notification'),
    path('news/', news_articles_list, name='admin-news-list'),
    path('news/<int:article_id>/', news_article_detail, name='admin-news-detail'),
    path('committee-codes/generate/', generate_committee_code, name='admin-generate-committee-code'),
    path('committee-codes/', list_committee_codes, name='admin-list-committee-codes'),
    path('committee-codes/<int:code_id>/delete/', delete_committee_code, name='admin-delete-committee-code'),
    path('committee-codes/<int:code_id>/archive/', archive_committee_code, name='admin-archive-committee-code'),
    path('committee-codes/<int:code_id>/restore/', restore_committee_code, name='admin-restore-committee-code'),
]