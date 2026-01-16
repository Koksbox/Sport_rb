# apps/attendance/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .serializers import AttendanceRecordSerializer, AttendanceMarkSerializer, AbsenceReasonSerializer
from apps.attendance.models import AttendanceRecord, AbsenceReason
from apps.training.models import TrainingGroup
from ...athletes.models import AthleteProfile


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_absence_reasons(request):
    """Список причин отсутствия"""
    reasons = AbsenceReason.objects.all()
    serializer = AbsenceReasonSerializer(reasons, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """Отметить посещаемость на дату"""
    serializer = AttendanceMarkSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        record = serializer.save()
        return Response(AttendanceRecordSerializer(record).data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_attendance(request, group_id):
    """Посещаемость группы за последние 30 дней"""
    try:
        group = TrainingGroup.objects.get(id=group_id)
        # Проверка доступа
        if not group.coach_memberships.filter(
            coach__user=request.user, status='active'
        ).exists():
            return Response({"error": "Нет доступа"}, status=403)

        start_date = timezone.now().date() - timedelta(days=30)
        records = AttendanceRecord.objects.filter(
            group=group,
            date__gte=start_date
        ).select_related('athlete__user', 'absence_reason')
        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data)
    except TrainingGroup.DoesNotExist:
        return Response({"error": "Группа не найдена"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_athlete_attendance(request, athlete_id):
    """Статистика посещаемости спортсмена (для родителя или самого спортсмена)"""
    try:
        athlete = AthleteProfile.objects.get(id=athlete_id)
        # Проверка: только владелец или родитель
        if request.user != athlete.user:
            # Проверка родительской связи
            if not request.user.parent_links.filter(
                child_profile=athlete, is_confirmed=True
            ).exists():
                return Response({"error": "Нет доступа"}, status=403)

        records = AttendanceRecord.objects.filter(
            athlete=athlete
        ).select_related('group', 'absence_reason').order_by('-date')
        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data)
    except AthleteProfile.DoesNotExist:
        return Response({"error": "Спортсмен не найден"}, status=404)