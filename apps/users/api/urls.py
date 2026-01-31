# apps/users/api/urls.py
from django.urls import path
from .views import (
    select_role, complete_profile, get_user_roles, switch_role, 
    get_user_basic_data, get_role_id, check_auto_link_roles, auto_link_roles
)
from .profile_views import search_by_role_id, view_profile_by_role_id

urlpatterns = [
    path('roles/', get_user_roles, name='user-roles'),
    path('roles/<str:role_name>/id/', get_role_id, name='user-role-id'),
    path('role-id/', get_role_id, name='user-current-role-id'),
    path('select-role/', select_role, name='user-select-role'),
    path('switch-role/', switch_role, name='user-switch-role'),
    path('complete-profile/', complete_profile, name='user-complete-profile'),
    path('basic-data/', get_user_basic_data, name='user-basic-data'),
    path('check-auto-link/', check_auto_link_roles, name='user-check-auto-link'),
    path('auto-link-roles/', auto_link_roles, name='user-auto-link-roles'),
    # Поиск и просмотр профилей
    path('search-by-role-id/', search_by_role_id, name='user-search-by-role-id'),
    path('profile/<str:role_id>/', view_profile_by_role_id, name='user-profile-by-role-id'),
]