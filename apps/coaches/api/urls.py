# apps/coaches/api/urls.py
from django.urls import path
from .views import (
    get_coach_groups, approve_athlete_enrollment, reject_athlete_enrollment, send_club_request,
    search_clubs, get_coach_profile, get_coach_organizations, get_organization_groups,
    get_free_organizations, get_coach_requests_for_director, approve_coach_request_by_director,
    reject_coach_request_by_director, get_free_coaches_for_director, send_coach_invitation,
    get_coach_invitations, accept_coach_invitation, reject_coach_invitation
)

urlpatterns = [
    path('profile/', get_coach_profile, name='coach-profile'),
    path('groups/', get_coach_groups, name='coach-groups'),
    path('organizations/', get_coach_organizations, name='coach-organizations'),
    path('organizations/<int:org_id>/groups/', get_organization_groups, name='coach-organization-groups'),
    path('enrollments/<int:enrollment_id>/approve/', approve_athlete_enrollment, name='coach-approve-enrollment'),
    path('enrollments/<int:enrollment_id>/reject/', reject_athlete_enrollment, name='coach-reject-enrollment'),
    path('clubs/search/', search_clubs, name='coach-search-clubs'),
    path('clubs/request/', send_club_request, name='coach-send-request'),
    # Новые маршруты для системы заявок и приглашений
    path('free-organizations/', get_free_organizations, name='coach-free-organizations'),
    path('invitations/', get_coach_invitations, name='coach-invitations'),
    path('invitations/<int:invitation_id>/accept/', accept_coach_invitation, name='coach-accept-invitation'),
    path('invitations/<int:invitation_id>/reject/', reject_coach_invitation, name='coach-reject-invitation'),
    # Маршруты для директора
    path('requests/', get_coach_requests_for_director, name='director-coach-requests'),
    path('requests/<int:request_id>/approve/', approve_coach_request_by_director, name='director-approve-request'),
    path('requests/<int:request_id>/reject/', reject_coach_request_by_director, name='director-reject-request'),
    path('free-coaches/', get_free_coaches_for_director, name='director-free-coaches'),
    path('invitations/send/', send_coach_invitation, name='director-send-invitation'),
]