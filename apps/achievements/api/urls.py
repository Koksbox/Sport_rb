# apps/achievements/api/urls.py
from django.urls import path
from .views import (
    list_achievements, delete_achievement,
    list_coach_achievements, delete_coach_achievement,
    list_ranks, list_gto_results
)

urlpatterns = [
    path('achievements/', list_achievements, name='achievements-list'),
    path('achievements/<int:achievement_id>/', delete_achievement, name='achievements-delete'),
    path('coaches/achievements/', list_coach_achievements, name='coach-achievements-list'),
    path('coaches/achievements/<int:achievement_id>/', delete_coach_achievement, name='coach-achievements-delete'),
    path('ranks/', list_ranks, name='ranks-list'),
    path('gto/', list_gto_results, name='gto-list'),
]