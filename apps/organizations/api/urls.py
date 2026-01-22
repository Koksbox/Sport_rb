# apps/organizations/api/urls.py
from django.urls import path
from .views import (
    list_organizations, create_organization, 
    moderate_organization, approve_coach_request,
    get_organization_detail, get_my_organizations
)

urlpatterns = [
    path('', list_organizations, name='organization-list'),
    path('my/', get_my_organizations, name='organization-my'),
    path('<int:org_id>/', get_organization_detail, name='organization-detail'),
    path('create/', create_organization, name='organization-create'),
    path('moderate/<int:org_id>/', moderate_organization, name='moderate-organization'),
    path('coach-requests/<int:request_id>/approve/', approve_coach_request, name='approve-coach-request'),
]