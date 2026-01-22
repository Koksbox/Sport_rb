# apps/users/api/urls.py
from django.urls import path
from .views import select_role, complete_profile, get_user_roles, switch_role, get_user_basic_data

urlpatterns = [
    path('roles/', get_user_roles, name='user-roles'),
    path('select-role/', select_role, name='user-select-role'),
    path('switch-role/', switch_role, name='user-switch-role'),
    path('complete-profile/', complete_profile, name='user-complete-profile'),
    path('basic-data/', get_user_basic_data, name='user-basic-data'),
]