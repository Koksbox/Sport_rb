# apps/parents/api/urls.py
from django.urls import path
from .views import request_child_link, get_children_list, get_child_profile

urlpatterns = [
    path('children/request/', request_child_link, name='parent-request-child'),
    path('children/', get_children_list, name='parent-children-list'),
    path('children/<int:child_id>/', get_child_profile, name='parent-child-profile'),
]