# apps/city_committee/api/urls.py
from django.urls import path
from .views import get_city_overview, get_organization_map, export_gis_data
from .committee_views import (
    get_organization_statistics, create_event, send_global_notification,
    register_committee_staff
)

urlpatterns = [
    path('overview/', get_city_overview, name='city-overview'),
    path('map/', get_organization_map, name='city-map'),
    path('gis/export/', export_gis_data, name='gis-export'),
    # Новые endpoints для сотрудников спорткомитета
    path('organizations/statistics/', get_organization_statistics, name='committee-org-statistics'),
    path('organizations/<int:organization_id>/statistics/', get_organization_statistics, name='committee-org-statistics-detail'),
    path('events/create/', create_event, name='committee-create-event'),
    path('notifications/global/', send_global_notification, name='committee-global-notification'),
    path('register/', register_committee_staff, name='committee-register'),
]