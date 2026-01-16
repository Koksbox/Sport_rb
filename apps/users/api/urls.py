# apps/users/api/urls.py
from django.urls import path
from .views import select_role

urlpatterns = [
    path('select-role/', select_role, name='user-select-role'),
]