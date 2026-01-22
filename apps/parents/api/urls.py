# apps/parents/api/urls.py
from django.urls import path
from .views import (
    request_child_link, get_children_list, get_child_profile,
    get_pending_requests, confirm_link, reject_link, get_my_role_id
)

urlpatterns = [
    path('children/request/', request_child_link, name='parent-request-child'),
    path('children/', get_children_list, name='parent-children-list'),
    path('children/<int:child_id>/', get_child_profile, name='parent-child-profile'),
    path('requests/', get_pending_requests, name='parent-pending-requests'),
    path('requests/<int:link_id>/confirm/', confirm_link, name='parent-confirm-link'),
    path('requests/<int:link_id>/reject/', reject_link, name='parent-reject-link'),
    path('my-role-id/', get_my_role_id, name='parent-my-role-id'),
]