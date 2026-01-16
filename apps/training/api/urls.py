# apps/training/api/urls.py
from django.urls import path
from .views import list_groups, list_age_levels, create_group

urlpatterns = [
    path('', list_groups, name='training-groups'),
    path('age-levels/', list_age_levels, name='training-age-levels'),
    path('create/', create_group, name='training-create-group'),
]