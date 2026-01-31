# apps/events/api/urls.py
from django.urls import path
from .views import (
    list_events, event_detail, register_for_event, cancel_registration,
    check_user_registration, event_participants,
    create_event, upload_event_results,
    get_available_athletes_for_event, get_available_groups_for_event,
    bulk_register_for_event, my_events
)
from .invitation_views import (
    create_invitations, get_user_invitations, respond_to_invitation
)

urlpatterns = [
    path('', list_events, name='event-list'),
    path('my/', my_events, name='event-my-events'),
    path('<int:event_id>/', event_detail, name='event-detail'),
    path('<int:event_id>/register/', register_for_event, name='event-register'),
    path('<int:event_id>/cancel/', cancel_registration, name='event-cancel-registration'),
    path('<int:event_id>/check-registration/', check_user_registration, name='event-check-registration'),
    path('<int:event_id>/participants/', event_participants, name='event-participants'),
    path('<int:event_id>/athletes/', get_available_athletes_for_event, name='event-available-athletes'),
    path('<int:event_id>/groups/', get_available_groups_for_event, name='event-available-groups'),
    path('<int:event_id>/bulk-register/', bulk_register_for_event, name='event-bulk-register'),
    path('create/', create_event, name='event-create'),
    path('<int:event_id>/results/upload/', upload_event_results, name='event-upload-results'),
    # Приглашения
    path('invitations/create/', create_invitations, name='event-invitations-create'),
    path('invitations/my/', get_user_invitations, name='event-invitations-my'),
    path('invitations/<int:invitation_id>/respond/', respond_to_invitation, name='event-invitation-respond'),
]