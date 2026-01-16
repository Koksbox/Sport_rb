# apps/training/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    TrainingGroupSerializer, TrainingGroupCreateSerializer,
    AgeLevelSerializer
)
from apps.training.models import TrainingGroup, AgeLevel
from apps.organizations.models import Organization

@api_view(['GET'])
def list_groups(request):
    """Список всех активных групп"""
    groups = TrainingGroup.objects.filter(is_active=True).select_related(
        'sport', 'age_level', 'organization'
    ).prefetch_related('schedules')
    serializer = TrainingGroupSerializer(groups, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def list_age_levels(request):
    """Список возрастных уровней"""
    levels = AgeLevel.objects.all()
    serializer = AgeLevelSerializer(levels, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    """Создать группу (только для директора)"""
    try:
        director = request.user.director_role
        org = director.organization
    except Exception:
        return Response({"error": "Только директор может создавать группы"}, status=status.HTTP_403_FORBIDDEN)

    serializer = TrainingGroupCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Привязываем к организации директора
        group = serializer.save(organization=org)
        return Response(TrainingGroupSerializer(group).data, status=201)
    return Response(serializer.errors, status=400)