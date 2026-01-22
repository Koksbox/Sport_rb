# apps/admin_rb/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .serializers import UserSerializer, AssignRoleSerializer
from apps.users.models import UserRole, CustomUser
from apps.organizations.models import Organization
from apps.athletes.models import AthleteProfile
from apps.coaches.models import CoachProfile
from apps.events.models import Event
from apps.attendance.models import AttendanceRecord
from apps.audit.models import AuditLog
from apps.audit.models.audit_log import ACTION_CHOICES

def check_admin_permission(user):
    """Проверка прав администратора"""
    return user.roles.filter(role='admin_rb').exists() or user.is_superuser

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Получить общую статистику для кабинета администратора"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    # Статистика пользователей
    total_users = CustomUser.objects.count()
    users_today = CustomUser.objects.filter(created_at__date=timezone.now().date()).count()
    users_this_week = CustomUser.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    users_this_month = CustomUser.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()
    
    # Статистика по ролям
    roles_stats = UserRole.objects.values('role').annotate(count=Count('id')).order_by('-count')
    
    # Статистика организаций
    total_orgs = Organization.objects.count()
    pending_orgs = Organization.objects.filter(status='pending').count()
    approved_orgs = Organization.objects.filter(status='approved').count()
    rejected_orgs = Organization.objects.filter(status='rejected').count()
    
    # Статистика спортсменов
    total_athletes = AthleteProfile.objects.count()
    
    # Статистика тренеров
    total_coaches = CoachProfile.objects.count()
    
    # Статистика мероприятий
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now()).count()
    past_events = Event.objects.filter(start_date__lt=timezone.now()).count()
    
    # Статистика посещаемости
    total_attendance = AttendanceRecord.objects.count()
    attended_count = AttendanceRecord.objects.filter(attended=True).count()
    attendance_rate = (attended_count / total_attendance * 100) if total_attendance > 0 else 0
    
    # Статистика за последние 30 дней
    last_30_days = timezone.now() - timedelta(days=30)
    new_users_30d = CustomUser.objects.filter(created_at__gte=last_30_days).count()
    new_orgs_30d = Organization.objects.filter(created_at__gte=last_30_days).count()
    new_events_30d = Event.objects.filter(created_at__gte=last_30_days).count()
    
    return Response({
        'users': {
            'total': total_users,
            'today': users_today,
            'this_week': users_this_week,
            'this_month': users_this_month,
            'last_30_days': new_users_30d,
            'by_role': list(roles_stats)
        },
        'organizations': {
            'total': total_orgs,
            'pending': pending_orgs,
            'approved': approved_orgs,
            'rejected': rejected_orgs,
            'last_30_days': new_orgs_30d
        },
        'athletes': {
            'total': total_athletes
        },
        'coaches': {
            'total': total_coaches
        },
        'events': {
            'total': total_events,
            'upcoming': upcoming_events,
            'past': past_events,
            'last_30_days': new_events_30d
        },
        'attendance': {
            'total_records': total_attendance,
            'attended': attended_count,
            'rate': round(attendance_rate, 2)
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_organizations(request):
    """Список организаций на модерации"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

    orgs = Organization.objects.filter(status='pending').select_related('created_by', 'city')
    data = []
    for org in orgs:
        data.append({
            'id': org.id,
            'name': org.name,
            'inn': org.inn,
            'city': org.city.name if org.city else None,
            'created_at': org.created_at,
            'created_by': UserSerializer(org.created_by).data if org.created_by else None
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_role(request):
    """Назначить роль (moderator / admin_rb)"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

    serializer = AssignRoleSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": f"Роль назначена пользователю {user.email}"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_logs(request):
    """Получить логи системы"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    # Получаем логи из файла и из БД
    from django.conf import settings
    import os
    
    logs_data = {
        'audit_logs': [],
        'django_logs': []
    }
    
    # Аудит логи из БД
    audit_logs = AuditLog.objects.select_related('user').order_by('-created_at')[:100]
    for log in audit_logs:
        action_display = dict(ACTION_CHOICES).get(log.action, log.action)
        logs_data['audit_logs'].append({
            'id': log.id,
            'user': log.user.email if log.user else 'Система',
            'action': action_display,
            'action_code': log.action,
            'timestamp': log.created_at,
            'ip_address': log.ip_address,
            'details': log.details
        })
    
    # Django логи из файла
    log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'django.log')
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Последние 100 строк
                logs_data['django_logs'] = [line.strip() for line in lines[-100:] if line.strip()]
        except Exception as e:
            logs_data['django_logs'] = [f'Ошибка чтения логов: {str(e)}']
    
    return Response(logs_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_list(request):
    """Список всех пользователей с фильтрацией"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    search = request.query_params.get('search', '')
    role_filter = request.query_params.get('role', '')
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    users = CustomUser.objects.all()
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if role_filter:
        users = users.filter(roles__role=role_filter).distinct()
    
    total = users.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    users_list = []
    for user in users[start:end]:
        user_roles = list(user.roles.values_list('role', flat=True))
        users_list.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'created_at': user.created_at,
            'is_active': user.is_active,
            'roles': user_roles
        })
    
    return Response({
        'total': total,
        'page': page,
        'page_size': page_size,
        'results': users_list
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_user_status(request, user_id):
    """Активировать/деактивировать пользователя"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return Response({
            'message': f'Пользователь {"активирован" if user.is_active else "деактивирован"}',
            'is_active': user.is_active
        })
    except CustomUser.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organizations_list(request):
    """Список всех организаций"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    status_filter = request.query_params.get('status', '')
    search = request.query_params.get('search', '')
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    orgs = Organization.objects.select_related('city', 'created_by').all()
    
    if status_filter:
        orgs = orgs.filter(status=status_filter)
    
    if search:
        orgs = orgs.filter(
            Q(name__icontains=search) |
            Q(inn__icontains=search)
        )
    
    total = orgs.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    orgs_list = []
    for org in orgs[start:end]:
        orgs_list.append({
            'id': org.id,
            'name': org.name,
            'inn': org.inn,
            'status': org.status,
            'city': org.city.name if org.city else None,
            'created_at': org.created_at,
            'created_by': UserSerializer(org.created_by).data if org.created_by else None
        })
    
    return Response({
        'total': total,
        'page': page,
        'page_size': page_size,
        'results': orgs_list
    })