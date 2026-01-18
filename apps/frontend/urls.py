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
    path('organizations/', views.organizations_list, name='frontend-organizations'),
    path('organizations/create/', views.organization_create, name='frontend-organization-create'),
    path('events/', views.events_list, name='frontend-events'),
    path('events/<int:event_id>/', views.event_detail_page, name='frontend-event-detail'),
]
