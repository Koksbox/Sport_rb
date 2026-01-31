# apps/achievements/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    AchievementSerializer, AchievementCreateSerializer,
    SportsRankSerializer, GtoResultSerializer,
    CoachAchievementSerializer, CoachAchievementCreateSerializer
)
from apps.achievements.models import Achievement, SportsRank, GtoResult, CoachAchievement

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_achievements(request):
    """Список достижений спортсмена или создание нового"""
    if request.method == 'GET':
        achievements = Achievement.objects.filter(athlete__user=request.user).select_related('event')
        serializer = AchievementSerializer(achievements, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Проверяем, что у пользователя есть профиль спортсмена
        if not hasattr(request.user, 'athlete_profile'):
            return Response(
                {'error': 'У вас нет профиля спортсмена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AchievementCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            achievement = serializer.save(athlete=request.user.athlete_profile)
            return Response(
                AchievementSerializer(achievement, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_achievement(request, achievement_id):
    """Удаление достижения"""
    try:
        achievement = Achievement.objects.get(id=achievement_id, athlete__user=request.user)
        achievement.delete()
        return Response({'message': 'Достижение удалено'}, status=status.HTTP_200_OK)
    except Achievement.DoesNotExist:
        return Response({'error': 'Достижение не найдено'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_coach_achievements(request):
    """Список достижений тренера или создание нового"""
    if request.method == 'GET':
        if not hasattr(request.user, 'coach_profile'):
            return Response(
                {'error': 'У вас нет профиля тренера'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        achievements = CoachAchievement.objects.filter(coach__user=request.user).select_related('event')
        serializer = CoachAchievementSerializer(achievements, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Проверяем, что у пользователя есть профиль тренера
        if not hasattr(request.user, 'coach_profile'):
            return Response(
                {'error': 'У вас нет профиля тренера'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CoachAchievementCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            achievement = serializer.save(coach=request.user.coach_profile)
            return Response(
                CoachAchievementSerializer(achievement, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_coach_achievement(request, achievement_id):
    """Удаление достижения тренера"""
    try:
        achievement = CoachAchievement.objects.get(id=achievement_id, coach__user=request.user)
        achievement.delete()
        return Response({'message': 'Достижение удалено'}, status=status.HTTP_200_OK)
    except CoachAchievement.DoesNotExist:
        return Response({'error': 'Достижение не найдено'}, status=status.HTTP_404_NOT_FOUND)

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
