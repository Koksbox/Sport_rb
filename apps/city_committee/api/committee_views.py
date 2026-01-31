# apps/city_committee/api/committee_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from apps.organizations.models import Organization
from apps.athletes.models import AthleteProfile
from apps.coaches.models import CoachProfile
from apps.events.models import Event
from apps.notifications.models import Notification
from apps.users.models import CustomUser
from apps.geography.models import City
from apps.city_committee.models import CommitteeStaff, CommitteeRegistrationCode
from apps.attendance.models import AttendanceRecord
from apps.training.models import TrainingGroup

def check_committee_staff(request):
    """Проверка, что пользователь является сотрудником спорткомитета"""
    if not request.user.is_authenticated:
        return None
    try:
        return request.user.committee_role
    except:
        return None

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_statistics(request, organization_id=None):
    """Статистика по организациям (для сотрудников спорткомитета)"""
    committee_staff = check_committee_staff(request)
    if not committee_staff:
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    city = committee_staff.city
    
    if organization_id:
        # Статистика по конкретной организации
        try:
            org = Organization.objects.get(id=organization_id, city=city, status='approved')
        except Organization.DoesNotExist:
            return Response({"error": "Организация не найдена"}, status=status.HTTP_404_NOT_FOUND)
        
        # Количество спортсменов в организации
        athletes_count = AthleteProfile.objects.filter(
            enrollments__group__organization=org,
            enrollments__status='active'
        ).distinct().count()
        
        # Количество тренеров
        coaches_count = CoachProfile.objects.filter(
            coach_memberships__organization=org,
            coach_memberships__status='active'
        ).distinct().count()
        
        # Количество групп
        groups_count = org.groups.filter(status='active').count()
        
        # Посещаемость за последний месяц
        month_ago = timezone.now() - timedelta(days=30)
        attendance_records = AttendanceRecord.objects.filter(
            group__organization=org,
            date__gte=month_ago
        )
        total_sessions = attendance_records.count()
        attended_sessions = attendance_records.filter(status='attended').count()
        attendance_rate = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Мероприятия организации
        events_count = Event.objects.filter(
            organizer_org=org,
            start_date__gte=timezone.now()
        ).count()
        
        return Response({
            'organization': {
                'id': org.id,
                'name': org.name,
                'city': org.city.name if org.city else None,
            },
            'statistics': {
                'athletes_count': athletes_count,
                'coaches_count': coaches_count,
                'groups_count': groups_count,
                'attendance_rate': round(attendance_rate, 2),
                'total_sessions': total_sessions,
                'attended_sessions': attended_sessions,
                'upcoming_events': events_count,
            }
        })
    else:
        # Список всех организаций с базовой статистикой
        organizations = Organization.objects.filter(
            city=city,
            status='approved'
        ).annotate(
            athletes_count=Count('groups__enrollments', filter=Q(groups__enrollments__status='active'), distinct=True),
            coaches_count=Count('coach_memberships', filter=Q(coach_memberships__status='active'), distinct=True),
            groups_count=Count('groups', filter=Q(groups__status='active'))
        )
        
        orgs_data = []
        for org in organizations:
            orgs_data.append({
                'id': org.id,
                'name': org.name,
                'org_type': org.org_type,
                'athletes_count': org.athletes_count or 0,
                'coaches_count': org.coaches_count or 0,
                'groups_count': org.groups_count or 0,
            })
        
        return Response({
            'city': city.name,
            'organizations': orgs_data,
            'total_organizations': len(orgs_data)
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    """Создание мероприятия сотрудником спорткомитета"""
    committee_staff = check_committee_staff(request)
    if not committee_staff:
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    city = committee_staff.city
    
    # Валидация данных
    required_fields = ['title', 'description', 'event_type', 'level', 'venue', 'start_date']
    for field in required_fields:
        if field not in request.data:
            return Response({"error": f"Поле {field} обязательно"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        event = Event.objects.create(
            title=request.data['title'],
            description=request.data['description'],
            event_type=request.data['event_type'],
            level=request.data['level'],
            city=city,
            venue=request.data['venue'],
            start_date=request.data['start_date'],
            end_date=request.data.get('end_date'),
            organizer_user=request.user,
            requires_registration=request.data.get('requires_registration', True),
            status=request.data.get('status', 'published')
        )
        
        return Response({
            "message": "Мероприятие успешно создано",
            "event_id": event.id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": f"Ошибка при создании мероприятия: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_global_notification(request):
    """Отправка глобального уведомления всем пользователям"""
    committee_staff = check_committee_staff(request)
    if not committee_staff:
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    # Валидация данных
    if 'title' not in request.data or 'body' not in request.data:
        return Response({"error": "Поля title и body обязательны"}, status=status.HTTP_400_BAD_REQUEST)
    
    title = request.data['title']
    body = request.data['body']
    notification_type = request.data.get('notification_type', 'mass_notification')
    
    # Получаем всех активных пользователей
    users = CustomUser.objects.filter(is_active=True)
    
    # Создаём уведомления для всех пользователей
    notifications = []
    for user in users:
        notifications.append(
            Notification(
                recipient=user,
                sender=request.user,
                notification_type=notification_type,
                title=title,
                body=body,
                is_read=False
            )
        )
    
    # Массовое создание уведомлений
    Notification.objects.bulk_create(notifications, batch_size=100)
    
    return Response({
        "message": f"Глобальное уведомление отправлено {len(notifications)} пользователям",
        "recipients_count": len(notifications)
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_committee_staff(request):
    """Регистрация сотрудника спорткомитета по специальному коду"""
    if 'registration_code' not in request.data:
        return Response({"error": "Код регистрации обязателен"}, status=status.HTTP_400_BAD_REQUEST)
    
    code = request.data['registration_code'].strip().upper()
    
    try:
        reg_code = CommitteeRegistrationCode.objects.get(
            code=code,
            is_active=True,
            is_used=False
        )
        
        # Проверка срока действия
        if reg_code.expires_at and reg_code.expires_at < timezone.now():
            return Response({"error": "Код регистрации истёк"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем или создаём город
        try:
            city = City.objects.get(name=reg_code.city_name)
        except City.DoesNotExist:
            # Создаём регион и город, если их нет
            from apps.geography.models import Region
            region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
            city = City.objects.create(name=reg_code.city_name, region=region, settlement_type='city')
        
        # Создаём роль сотрудника спорткомитета
        from apps.users.models import UserRole
        user_role, created = UserRole.objects.get_or_create(
            user=request.user,
            role='committee_staff',
            defaults={'is_active': True}
        )
        
        # Создаём профиль сотрудника спорткомитета
        committee_staff, created = CommitteeStaff.objects.get_or_create(
            user=request.user,
            defaults={'city': city}
        )
        
        # Отмечаем код как использованный
        reg_code.is_used = True
        reg_code.used_by_email = request.user.email
        reg_code.used_at = timezone.now()
        reg_code.save()
        
        # Устанавливаем активную роль
        request.session['active_role'] = 'committee_staff'
        
        return Response({
            "message": "Регистрация успешна",
            "role": "committee_staff",
            "city": city.name,
            "department": reg_code.department
        }, status=status.HTTP_201_CREATED)
        
    except CommitteeRegistrationCode.DoesNotExist:
        return Response({"error": "Неверный или неактивный код регистрации"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Ошибка регистрации: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
