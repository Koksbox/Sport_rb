# apps/coaches/api/urls.py
from django.urls import path
from .views import get_coach_groups, approve_athlete_enrollment, reject_athlete_enrollment, send_club_request, \
    search_clubs

urlpatterns = [
    path('groups/', get_coach_groups, name='coach-groups'),
    path('enrollments/<int:enrollment_id>/approve/', approve_athlete_enrollment, name='coach-approve-enrollment'),
    path('enrollments/<int:enrollment_id>/reject/', reject_athlete_enrollment, name='coach-reject-enrollment'),
    path('clubs/search/', search_clubs, name='coach-search-clubs'),
    path('clubs/request/', send_club_request, name='coach-send-request'),
]