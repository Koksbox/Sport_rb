# apps/admin_rb/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .serializers import UserSerializer, AssignRoleSerializer, NotificationCreateSerializer, NewsArticleSerializer
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
    if not user or not user.is_authenticated:
        return False
    return user.roles.filter(role='admin_rb', is_active=True).exists() or user.is_superuser

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
    try:
        total_attendance = AttendanceRecord.objects.count()
        attended_count = AttendanceRecord.objects.filter(attended=True).count()
        attendance_rate = (attended_count / total_attendance * 100) if total_attendance > 0 else 0
    except Exception:
        total_attendance = 0
        attended_count = 0
        attendance_rate = 0
    
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notification(request):
    """Создание уведомлений для пользователей с фильтрацией"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    from .serializers import NotificationCreateSerializer
    from apps.events.models import EventRegistration
    
    serializer = NotificationCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    title = data['title']
    body = data['body']
    notification_type = data.get('notification_type', 'mass_notification')
    
    # Определяем получателей
    recipients = CustomUser.objects.filter(is_active=True)
    
    if data.get('target_all'):
        # Все пользователи
        pass
    elif data.get('target_roles'):
        # Фильтр по ролям
        roles = data['target_roles']
        recipients = recipients.filter(roles__role__in=roles, roles__is_active=True).distinct()
    elif data.get('target_event_id'):
        # Участники мероприятия
        event_id = data['target_event_id']
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Мероприятие не найдено"}, status=status.HTTP_404_NOT_FOUND)
        
        # Получаем всех зарегистрированных участников
        registrations = EventRegistration.objects.filter(event=event, status='registered').select_related('athlete__user', 'coach__user')
        user_ids = set()
        for reg in registrations:
            if reg.athlete and reg.athlete.user:
                user_ids.add(reg.athlete.user.id)
            elif reg.coach and reg.coach.user:
                user_ids.add(reg.coach.user.id)
        recipients = recipients.filter(id__in=user_ids)
    else:
        return Response({"error": "Необходимо указать получателей"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Создаём уведомления
    notifications = []
    for user in recipients:
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
    
    # Массовое создание
    Notification.objects.bulk_create(notifications, batch_size=100)
    
    return Response({
        "message": f"Уведомление отправлено {len(notifications)} пользователям",
        "recipients_count": len(notifications)
    }, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def news_articles_list(request):
    """Список новостных статей (GET) или создание (POST)"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    from apps.core.models.news import NewsArticle
    from .serializers import NewsArticleSerializer
    
    if request.method == 'GET':
        articles = NewsArticle.objects.all().order_by('-created_at')
        serializer = NewsArticleSerializer(articles, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = NewsArticleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            article = serializer.save()
            return Response(NewsArticleSerializer(article).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def news_article_detail(request, article_id):
    """Детали, редактирование или удаление новостной статьи"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    from apps.core.models.news import NewsArticle
    from .serializers import NewsArticleSerializer
    
    try:
        article = NewsArticle.objects.get(id=article_id)
    except NewsArticle.DoesNotExist:
        return Response({"error": "Статья не найдена"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = NewsArticleSerializer(article)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = NewsArticleSerializer(article, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        article.delete()
        return Response({"message": "Статья удалена"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_committee_code(request):
    """Генерация кодов регистрации для сотрудников спорткомитета"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    from .serializers import CommitteeCodeGenerateSerializer
    from apps.city_committee.models import CommitteeRegistrationCode
    from django.utils import timezone
    from datetime import timedelta
    import random
    import string
    
    serializer = CommitteeCodeGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    city_name = data['city_name']
    count = data['count']
    department = data.get('department', '')
    position = data.get('position', '')
    expires_days = data.get('expires_days')
    code_length = data.get('code_length', 8)
    
    # Определяем срок действия
    expires_at = None
    if expires_days:
        expires_at = timezone.now() + timedelta(days=expires_days)
    
    created_codes = []
    for i in range(count):
        # Генерируем уникальный код
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
            if not CommitteeRegistrationCode.objects.filter(code=code).exists():
                break
        
        # Создаём код
        reg_code = CommitteeRegistrationCode.objects.create(
            code=code,
            city_name=city_name,
            department=department,
            position=position,
            issued_by=request.user.get_full_name() or request.user.email,
            expires_at=expires_at,
            is_active=True,
            is_used=False
        )
        
        created_codes.append({
            'id': reg_code.id,
            'code': reg_code.code,
            'city_name': reg_code.city_name,
            'department': reg_code.department,
            'position': reg_code.position,
            'expires_at': reg_code.expires_at,
            'created_at': reg_code.created_at
        })
    
    return Response({
        "message": f"Создано {len(created_codes)} кодов регистрации",
        "codes": created_codes
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_committee_codes(request):
    """Список кодов регистрации спорткомитета"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    from apps.city_committee.models import CommitteeRegistrationCode
    
    status_filter = request.query_params.get('status', '')  # 'active', 'used', 'all'
    city_filter = request.query_params.get('city', '')
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    codes = CommitteeRegistrationCode.objects.all().order_by('-created_at')
    
    if status_filter == 'active':
        codes = codes.filter(is_active=True, is_used=False)
    elif status_filter == 'used':
        codes = codes.filter(is_used=True)
    
    if city_filter:
        codes = codes.filter(city_name__icontains=city_filter)
    
    total = codes.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    codes_list = []
    for code in codes[start:end]:
        codes_list.append({
            'id': code.id,
            'code': code.code,
            'city_name': code.city_name,
            'department': code.department,
            'position': code.position,
            'issued_by': code.issued_by,
            'is_used': code.is_used,
            'is_active': code.is_active,
            'used_by_email': code.used_by_email,
            'used_at': code.used_at,
            'expires_at': code.expires_at,
            'created_at': code.created_at
        })
    
    return Response({
        'total': total,
        'page': page,
        'page_size': page_size,
        'results': codes_list
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_committee_code(request, code_id):
    """Удаление кода регистрации спорткомитета"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        code = CommitteeRegistrationCode.objects.get(id=code_id)
    except CommitteeRegistrationCode.DoesNotExist:
        return Response({"error": "Код не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    # Проверяем, не использован ли код
    if code.is_used:
        return Response({"error": "Нельзя удалить использованный код"}, status=status.HTTP_400_BAD_REQUEST)
    
    code.delete()
    return Response({"message": "Код успешно удалён"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_committee_code(request, code_id):
    """Архивирование кода регистрации спорткомитета"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        code = CommitteeRegistrationCode.objects.get(id=code_id)
    except CommitteeRegistrationCode.DoesNotExist:
        return Response({"error": "Код не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    code.is_active = False
    code.save()
    return Response({"message": "Код успешно архивирован"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_committee_code(request, code_id):
    """Восстановление кода регистрации спорткомитета из архива"""
    if not check_admin_permission(request.user):
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        code = CommitteeRegistrationCode.objects.get(id=code_id)
    except CommitteeRegistrationCode.DoesNotExist:
        return Response({"error": "Код не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    code.is_active = True
    code.save()
    return Response({"message": "Код успешно восстановлен"}, status=status.HTTP_200_OK)