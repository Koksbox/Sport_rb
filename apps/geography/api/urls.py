# apps/geography/api/urls.py
from django.urls import path
from .views import list_regions, list_cities, list_districts

urlpatterns = [
    path('regions/', list_regions, name='geography-regions'),
    path('cities/', list_cities, name='geography-cities'),
    path('districts/', list_districts, name='geography-districts'),
]