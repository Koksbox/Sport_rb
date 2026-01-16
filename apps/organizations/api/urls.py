# apps/organizations/api/urls.py
from django.urls import path
from .views import moderate_organization, approve_coach_request

urlpatterns = [
    path('moderate/<int:org_id>/', moderate_organization, name='moderate-organization'),
    path('coach-requests/<int:request_id>/approve/', approve_coach_request, name='approve-coach-request'),

]