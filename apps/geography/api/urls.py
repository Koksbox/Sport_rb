# apps/geography/api/urls.py
from django.urls import path
from .views import list_regions, list_cities, list_districts, search_cities

urlpatterns = [
    path('regions/', list_regions, name='geography-regions'),
    path('cities/', list_cities, name='geography-cities'),
    path('cities/search/', search_cities, name='geography-cities-search'),
    path('districts/', list_districts, name='geography-districts'),
]