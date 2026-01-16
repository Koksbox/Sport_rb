# apps/achievements/api/urls.py
from django.urls import path
from .views import list_achievements, list_ranks, list_gto_results

urlpatterns = [
    path('achievements/', list_achievements, name='achievements-list'),
    path('ranks/', list_ranks, name='ranks-list'),
    path('gto/', list_gto_results, name='gto-list'),
]