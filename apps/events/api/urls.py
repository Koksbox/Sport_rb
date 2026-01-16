# apps/events/api/urls.py
from django.urls import path
from .views import (
    list_events, event_detail, register_for_event,
    create_event, upload_event_results
)

urlpatterns = [
    path('', list_events, name='event-list'),
    path('<int:event_id>/', event_detail, name='event-detail'),
    path('<int:event_id>/register/', register_for_event, name='event-register'),
    path('create/', create_event, name='event-create'),
    path('<int:event_id>/results/upload/', upload_event_results, name='event-upload-results'),
]