# apps/city_committee/api/urls.py
from django.urls import path
from .views import get_city_overview, get_organization_map, export_gis_data

urlpatterns = [
    path('overview/', get_city_overview, name='city-overview'),
    path('map/', get_organization_map, name='city-map'),
    path('gis/export/', export_gis_data, name='gis-export'),
]