# apps/athletes/api/urls.py
from django.urls import path
from .views import get_athlete_profile, get_parent_requests, confirm_parent_request, \
    reject_parent_request, search_clubs_for_athlete, request_enrollment, get_athlete_progress, \
    request_section_enrollment

urlpatterns = [
    path('profile/', get_athlete_profile, name='athlete-profile'),  # GET и PATCH

    # Новое: управление запросами от родителей
    path('parent-requests/', get_parent_requests, name='athlete-parent-requests'),
    path('parent-requests/<int:request_id>/confirm/', confirm_parent_request, name='athlete-confirm-parent'),
    path('parent-requests/<int:request_id>/reject/', reject_parent_request, name='athlete-reject-parent'),
    path('clubs/search/', search_clubs_for_athlete, name='athlete-search-clubs'),
    path('enrollment/request/', request_enrollment, name='athlete-request-enrollment'),
    path('section-enrollment/request/', request_section_enrollment, name='athlete-section-enrollment-request'),
    path('progress/', get_athlete_progress, name='athlete-progress'),

]