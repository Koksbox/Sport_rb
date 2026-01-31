# apps/organizations/api/urls.py
from django.urls import path
from .views import (
    list_organizations, create_organization, 
    moderate_organization, approve_coach_request,
    get_organization_detail, get_my_organizations
)
from .organization_role_views import (
    create_organization_role_request,
    get_my_organization_role_request,
    list_organization_role_requests,
    review_organization_role_request
)

urlpatterns = [
    path('', list_organizations, name='organization-list'),
    path('my/', get_my_organizations, name='organization-my'),
    path('<int:org_id>/', get_organization_detail, name='organization-detail'),
    path('create/', create_organization, name='organization-create'),
    path('moderate/<int:org_id>/', moderate_organization, name='moderate-organization'),
    path('coach-requests/<int:request_id>/approve/', approve_coach_request, name='approve-coach-request'),
    # Заявки на роль организации
    path('role-request/', create_organization_role_request, name='organizations-role-request-create'),
    path('role-request/my/', get_my_organization_role_request, name='organizations-role-request-my'),
    path('role-requests/', list_organization_role_requests, name='organizations-role-requests-list'),
    path('role-requests/<int:request_id>/review/', review_organization_role_request, name='organizations-role-request-review'),
]