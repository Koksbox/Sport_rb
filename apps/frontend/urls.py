# apps/frontend/urls.py
from django.urls import path
from . import views
from . import views_auth

urlpatterns = [
    path('', views.index, name='frontend-index'),
    path('login/', views.login_page, name='frontend-login'),
    path('accounts/login/', views_auth.django_login, name='django-login'),  # Для совместимости с login_required
    path('register/', views.register_page, name='frontend-register'),
    path('dashboard/', views.dashboard, name='frontend-dashboard'),
    path('role-selection/', views.role_selection, name='frontend-role-selection'),
    path('role-selection/new/', views.new_role_selection, name='frontend-new-role-selection'),
    path('organizations/', views.organizations_list, name='frontend-organizations'),
    path('organizations/<int:org_id>/', views.organization_detail, name='frontend-organization-detail'),
    path('organizations/create/', views.organization_create, name='frontend-organization-create'),
    path('organizations/my/', views.my_organizations, name='frontend-my-organizations'),
    path('events/', views.events_list, name='frontend-events'),
    path('events/<int:event_id>/', views.event_detail_page, name='frontend-event-detail'),
    path('athletes/profile/edit/', views.athlete_profile_edit, name='frontend-athlete-profile-edit'),
    path('coaches/profile/edit/', views.coach_profile_edit, name='frontend-coach-profile-edit'),
    path('coaches/organizations/find/', views.coach_find_organization, name='frontend-coach-find-organization'),
    path('coaches/organizations/<int:org_id>/groups/', views.coach_organization_groups, name='frontend-coach-organization-groups'),
    path('coaches/groups/', views.coach_groups_list, name='frontend-coach-groups'),
    path('coaches/groups/<int:group_id>/', views.coach_group_detail, name='frontend-coach-group-detail'),
    path('coaches/invitations/', views.coach_invitations, name='frontend-coach-invitations'),
    path('director/coach-requests/', views.director_coach_requests, name='frontend-director-coach-requests'),
    path('director/free-coaches/', views.director_free_coaches, name='frontend-director-free-coaches'),
    path('users/basic-data/edit/', views.user_basic_data_edit, name='frontend-user-basic-data-edit'),
    path('parents/profile/edit/', views.parent_profile_edit, name='frontend-parent-profile-edit'),
    path('parents/children/', views.parent_children_list, name='frontend-parent-children'),
    path('parents/children/<int:child_id>/', views.parent_child_detail, name='frontend-parent-child-detail'),
    path('parents/requests/', views.parent_requests, name='frontend-parent-requests'),
    path('admin/', views.admin_dashboard, name='frontend-admin-dashboard'),
    path('logout/', views.logout_view, name='frontend-logout'),
]
