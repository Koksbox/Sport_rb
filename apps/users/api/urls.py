# apps/users/api/urls.py
from django.urls import path
from .views import select_role, complete_profile

urlpatterns = [
    path('select-role/', select_role, name='user-select-role'),
    path('complete-profile/', complete_profile, name='user-complete-profile'),
]