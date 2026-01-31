# apps/analytics/api/urls.py
from django.urls import path
from .views import (
    population_coverage_report,
    sport_activity_report,
    export_to_excel,
    track_event,
    track_batch
)

urlpatterns = [
    path('reports/population/', population_coverage_report, name='analytics-population'),
    path('reports/sport-activity/', sport_activity_report, name='analytics-sport-activity'),
    path('export/<str:report_type>/excel/', export_to_excel, name='analytics-export-excel'),
    path('track/', track_event, name='analytics-track'),
    path('track-batch/', track_batch, name='analytics-track-batch'),
]