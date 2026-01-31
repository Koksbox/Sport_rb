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
        
        # Проверяем, первое ли это посещение спортсменом этой группы
        previous_attendance = AttendanceRecord.objects.filter(
            athlete=record.athlete,
            group=record.group
        ).exclude(id=record.id).exists()
        
        # Если это первое посещение и у спортсмена есть медицинские данные
        if not previous_attendance and record.status == 'present':
            try:
                from apps.athletes.models import MedicalInfo
                from apps.notifications.models import Notification
                from apps.organizations.staff import CoachMembership
                
                # Проверяем наличие медицинских данных
                has_medical_data = False
                try:
                    medical_info = record.athlete.medical_info
                    has_medical_data = (
                        (medical_info.conditions and len(medical_info.conditions) > 0) or 
                        (medical_info.other_conditions and medical_info.other_conditions.strip()) or 
                        (medical_info.allergies and medical_info.allergies.strip()) or
                        record.athlete.health_group
                    )
                except MedicalInfo.DoesNotExist:
                    # Если medical_info не создан, проверяем только health_group
                    has_medical_data = bool(record.athlete.health_group)
                
                if has_medical_data:
                    # Отправляем уведомление всем тренерам группы
                    coaches = CoachMembership.objects.filter(
                        organization=record.group.organization,
                        status='active'
                    ).select_related('coach__user')
                    
                    athlete_name = record.athlete.user.get_full_name() or 'Спортсмен'
                    group_name = record.group.name
                    
                    for membership in coaches:
                        Notification.objects.create(
                            recipient=membership.coach.user,
                            notification_type='athlete_medical_info',
                            title='Ознакомьтесь с медицинскими данными ученика',
                            body=f'Спортсмен {athlete_name} впервые посетил группу "{group_name}". У него есть медицинские данные, которые требуют внимания.'
                        )
            except Exception as e:
                # Логируем ошибку, но не прерываем процесс
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Ошибка при отправке уведомления тренеру: {str(e)}')
        
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_attendance_stats(request, group_id):
    """Статистика посещаемости группы"""
    try:
        group = TrainingGroup.objects.get(id=group_id)
        # Проверка доступа
        if not group.coach_memberships.filter(
            coach__user=request.user, status='active'
        ).exists():
            return Response({"error": "Нет доступа"}, status=403)

        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Статистика за последние 30 дней
        start_date = timezone.now().date() - timedelta(days=30)
        records = AttendanceRecord.objects.filter(
            group=group,
            date__gte=start_date
        )
        
        total_records = records.count()
        present_count = records.filter(status='present').count()
        absent_count = records.filter(status='absent').count()
        late_count = records.filter(status='late').count()
        
        # Статистика по спортсменам
        athletes_stats = []
        enrollments = group.enrollments.filter(status='active')
        for enrollment in enrollments:
            athlete = enrollment.athlete
            athlete_records = records.filter(athlete=athlete)
            athlete_total = athlete_records.count()
            athlete_present = athlete_records.filter(status='present').count()
            attendance_rate = (athlete_present / athlete_total * 100) if athlete_total > 0 else 0
            
            # Получаем ID роли спортсмена
            athlete_role_id = None
            try:
                athlete_role = athlete.user.roles.filter(role='athlete', is_active=True).first()
                athlete_role_id = athlete_role.unique_id if athlete_role and athlete_role.unique_id else None
            except:
                pass
            
            athletes_stats.append({
                'athlete_id': athlete.id,
                'athlete_name': athlete.user.get_full_name(),
                'athlete_role_id': athlete_role_id,
                'total': athlete_total,
                'present': athlete_present,
                'absent': athlete_records.filter(status='absent').count(),
                'late': athlete_records.filter(status='late').count(),
                'attendance_rate': round(attendance_rate, 1)
            })
        
        return Response({
            'group_id': group.id,
            'group_name': group.name,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': timezone.now().date().isoformat(),
                'days': 30
            },
            'overall': {
                'total': total_records,
                'present': present_count,
                'absent': absent_count,
                'late': late_count,
                'attendance_rate': round((present_count / total_records * 100) if total_records > 0 else 0, 1)
            },
            'athletes': athletes_stats
        })
    except TrainingGroup.DoesNotExist:
        return Response({"error": "Группа не найдена"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_attendance_stats(request, org_id):
    """Статистика посещаемости по всей организации"""
    try:
        from apps.organizations.models import Organization
        from apps.organizations.staff.coach_membership import CoachMembership
        
        organization = Organization.objects.get(id=org_id)
        coach = request.user.coach_profile
        
        # Проверка доступа
        if not CoachMembership.objects.filter(
            coach=coach, organization=organization, status='active'
        ).exists():
            return Response({"error": "Нет доступа"}, status=403)
        
        from django.db.models import Count, Q
        from datetime import timedelta
        
        start_date = timezone.now().date() - timedelta(days=30)
        
        # Получаем все группы организации, где тренер работает
        memberships = CoachMembership.objects.filter(
            coach=coach, organization=organization, status='active'
        )
        groups = []
        for membership in memberships:
            groups.extend(membership.groups.all())
        
        if not groups:
            return Response({
                'organization_id': org_id,
                'organization_name': organization.name,
                'groups': [],
                'overall': {
                    'total': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'attendance_rate': 0
                }
            })
        
        # Статистика по группам
        groups_stats = []
        total_records = 0
        total_present = 0
        total_absent = 0
        total_late = 0
        
        for group in groups:
            records = AttendanceRecord.objects.filter(
                group=group, date__gte=start_date
            )
            group_total = records.count()
            group_present = records.filter(status='present').count()
            group_absent = records.filter(status='absent').count()
            group_late = records.filter(status='late').count()
            
            groups_stats.append({
                'group_id': group.id,
                'group_name': group.name,
                'total': group_total,
                'present': group_present,
                'absent': group_absent,
                'late': group_late,
                'attendance_rate': round((group_present / group_total * 100) if group_total > 0 else 0, 1)
            })
            
            total_records += group_total
            total_present += group_present
            total_absent += group_absent
            total_late += group_late
        
        return Response({
            'organization_id': org_id,
            'organization_name': organization.name,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': timezone.now().date().isoformat(),
                'days': 30
            },
            'groups': groups_stats,
            'overall': {
                'total': total_records,
                'present': total_present,
                'absent': total_absent,
                'late': total_late,
                'attendance_rate': round((total_present / total_records * 100) if total_records > 0 else 0, 1)
            }
        })
    except Organization.DoesNotExist:
        return Response({"error": "Организация не найдена"}, status=404)