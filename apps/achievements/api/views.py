# apps/achievements/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import AchievementSerializer, SportsRankSerializer, GtoResultSerializer
from apps.achievements.models import Achievement, SportsRank, GtoResult

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_achievements(request):
    """Список достижений спортсмена"""
    achievements = Achievement.objects.filter(athlete__user=request.user)
    return Response(AchievementSerializer(achievements, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_ranks(request):
    """Список спортивных разрядов"""
    ranks = SportsRank.objects.filter(athlete__user=request.user)
    return Response(SportsRankSerializer(ranks, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_gto_results(request):
    """Результаты ГТО"""
    results = GtoResult.objects.filter(athlete__user=request.user)
    return Response(GtoResultSerializer(results, many=True).data)