# apps/attendance/api/urls.py
from django.urls import path
from .views import (
    get_absence_reasons, mark_attendance,
    get_group_attendance, get_athlete_attendance
)

urlpatterns = [
    path('reasons/', get_absence_reasons, name='attendance-reasons'),
    path('mark/', mark_attendance, name='attendance-mark'),
    path('group/<int:group_id>/', get_group_attendance, name='attendance-group'),
    path('athlete/<int:athlete_id>/', get_athlete_attendance, name='attendance-athlete'),
]