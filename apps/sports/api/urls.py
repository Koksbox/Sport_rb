# apps/sports/api/urls.py
from django.urls import path
from .views import list_sports, list_categories

urlpatterns = [
    path('', list_sports, name='sports-list'),
    path('<int:sport_id>/categories/', list_categories, name='sport-categories'),
]