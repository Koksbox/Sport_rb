# apps/events/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .serializers import (
    EventSerializer, EventCreateSerializer,
    EventRegistrationSerializer, EventResultSerializer
)
from apps.events.models import Event, EventRegistration, EventResult

# === Список мероприятий ===
@api_view(['GET'])
@permission_classes([AllowAny])
def list_events(request):
    """Список опубликованных мероприятий с пагинацией"""
    try:
        events = Event.objects.filter(status='published').select_related('city', 'organizer_org', 'organizer_user').prefetch_related('age_groups', 'categories')
        
        # Фильтры
        city = request.query_params.get('city')
        sport = request.query_params.get('sport')
        search = request.query_params.get('search', '').strip()
        event_type = request.query_params.get('event_type')
        upcoming = request.query_params.get('upcoming', '').lower() == 'true'
        past = request.query_params.get('past', '').lower() == 'true'
        sort_by = request.query_params.get('sort', 'start_date')  # start_date, title, city
        order = request.query_params.get('order', 'desc')  # asc, desc
        
        if city:
            events = events.filter(city__name__icontains=city)
        
        if sport:
            events = events.filter(sport__name__icontains=sport)
        
        if event_type:
            events = events.filter(event_type=event_type)
        
        if search:
            events = events.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(venue__icontains=search)
            )
        
        # Фильтр по дате
        now = timezone.now()
        if upcoming:
            events = events.filter(start_date__gte=now)
        elif past:
            events = events.filter(start_date__lt=now)
        
        # Сортировка
        sort_field = sort_by
        if sort_by == 'start_date':
            sort_field = 'start_date'
        elif sort_by == 'title':
            sort_field = 'title'
        elif sort_by == 'city':
            sort_field = 'city__name'
        else:
            sort_field = 'start_date'
        
        if order == 'desc':
            sort_field = f'-{sort_field}'
        
        events = events.order_by(sort_field)
        
        # Пагинация
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 12))
        total = events.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_events = events[start:end]
        serializer = EventSerializer(paginated_events, many=True)
        
        return Response({
            'results': serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'has_next': end < total,
            'has_previous': page > 1
        })
    except Exception as e:
        import traceback
        print(f"Error in list_events: {e}")
        print(traceback.format_exc())
        return Response({
            'error': 'Ошибка при загрузке мероприятий',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === Мои мероприятия ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_events(request):
    """Список мероприятий, на которые зарегистрирован пользователь"""
    try:
        user = request.user
        registrations = []
        
        # Регистрации как спортсмен
        if hasattr(user, 'athlete_profile'):
            athlete_regs = EventRegistration.objects.filter(
                registration_type='athlete',
                athlete=user.athlete_profile,
                status__in=['registered', 'confirmed']
            ).select_related('event', 'event__city', 'athlete', 'athlete__user')
            registrations.extend(list(athlete_regs))
        
        # Регистрации как тренер
        if hasattr(user, 'coach_profile'):
            coach_regs = EventRegistration.objects.filter(
                registration_type='coach',
                coach=user.coach_profile,
                status__in=['registered', 'confirmed']
            ).select_related('event', 'event__city', 'coach', 'coach__user')
            registrations.extend(list(coach_regs))
        
        # Формируем список мероприятий
        events_data = []
        for reg in registrations:
            try:
                event_serializer = EventSerializer(reg.event)
                reg_serializer = EventRegistrationSerializer(reg)
                events_data.append({
                    'event': event_serializer.data,
                    'registration': reg_serializer.data
                })
            except Exception as e:
                # Пропускаем проблемные регистрации
                continue
        
        return Response({"events": events_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

# === Детали мероприятия ===
@api_view(['GET'])
@permission_classes([AllowAny])
def event_detail(request, event_id):
    """Детали мероприятия"""
    try:
        event = Event.objects.get(id=event_id, status='published')
        serializer = EventSerializer(event)
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)


# === Регистрация спортсмена ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_for_event(request, event_id):
    """Спортсмен регистрируется на мероприятие"""
    import logging
    from django.db import transaction
    from rest_framework import status as http_status
    
    logger = logging.getLogger(__name__)
    
    try:
        # Проверяем наличие профиля спортсмена
        if not hasattr(request.user, 'athlete_profile'):
            return Response(
                {"error": "У вас нет профиля спортсмена"}, 
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        athlete = request.user.athlete_profile
        
        try:
            event = Event.objects.get(id=event_id, status='published')
        except Event.DoesNotExist:
            return Response(
                {"error": "Мероприятие не найдено или не опубликовано"}, 
                status=http_status.HTTP_404_NOT_FOUND
            )

        # Проверка возраста
        if not athlete.user.birth_date:
            return Response(
                {"error": "Укажите дату рождения в профиле"}, 
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        age = timezone.now().year - athlete.user.birth_date.year
        if timezone.now().month < athlete.user.birth_date.month or \
           (timezone.now().month == athlete.user.birth_date.month and timezone.now().day < athlete.user.birth_date.day):
            age -= 1
        
        eligible = event.age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
        if not eligible:
            # Формируем список допустимых возрастных групп
            age_groups_text = []
            for ag in event.age_groups.all():
                if ag.min_age == ag.max_age:
                    age_groups_text.append(f"{ag.min_age} лет")
                else:
                    age_groups_text.append(f"{ag.min_age}-{ag.max_age} лет")
            
            age_requirement = ", ".join(age_groups_text) if age_groups_text else "не указаны"
            return Response({
                "error": f"Возраст не соответствует требованиям. Ваш возраст: {age} лет. Требуемый возраст: {age_requirement}"
            }, status=http_status.HTTP_400_BAD_REQUEST)

        # Используем транзакцию для атомарности
        with transaction.atomic():
            registration, created = EventRegistration.objects.get_or_create(
                event=event,
                registration_type='athlete',
                athlete=athlete,
                defaults={'status': 'registered'}
            )
            if not created:
                if registration.status == 'cancelled':
                    registration.status = 'registered'
                    registration.save(update_fields=['status'])
                else:
                    return Response(
                        {"error": "Вы уже зарегистрированы"}, 
                        status=http_status.HTTP_400_BAD_REQUEST
                    )

        return Response({
            "message": "Регистрация успешна!",
            "registration_id": registration.id
        }, status=http_status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f'Ошибка при регистрации на мероприятие {event_id}: {str(e)}', exc_info=True)
        return Response(
            {"error": "Произошла ошибка при регистрации. Попробуйте позже."}, 
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# === Отмена регистрации ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_registration(request, event_id):
    """Отмена регистрации на мероприятие"""
    try:
        event = Event.objects.get(id=event_id)
        athlete = request.user.athlete_profile
        
        try:
            registration = EventRegistration.objects.get(event=event, athlete=athlete)
            if registration.status == 'cancelled':
                return Response({"error": "Регистрация уже отменена"}, status=400)
            
            registration.status = 'cancelled'
            registration.save()
            
            return Response({"message": "Регистрация отменена"})
        except EventRegistration.DoesNotExist:
            return Response({"error": "Вы не зарегистрированы на это мероприятие"}, status=404)
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# === Проверка регистрации пользователя ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_registration(request, event_id):
    """Проверка, зарегистрирован ли пользователь на мероприятие"""
    try:
        event = Event.objects.get(id=event_id)
        user = request.user
        
        registration = None
        
        # Проверяем регистрацию как спортсмен
        if hasattr(user, 'athlete_profile'):
            try:
                registration = EventRegistration.objects.get(
                    event=event,
                    registration_type='athlete',
                    athlete=user.athlete_profile
                )
            except EventRegistration.DoesNotExist:
                pass
        
        # Проверяем регистрацию как тренер
        if not registration and hasattr(user, 'coach_profile'):
            try:
                registration = EventRegistration.objects.get(
                    event=event,
                    registration_type='coach',
                    coach=user.coach_profile
                )
            except EventRegistration.DoesNotExist:
                pass
        
        if registration:
            serializer = EventRegistrationSerializer(registration)
            return Response({
                "is_registered": True,
                "registration": serializer.data
            })
        else:
            return Response({
                "is_registered": False,
                "registration": None
            })
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# === Список участников мероприятия ===
@api_view(['GET'])
@permission_classes([AllowAny])
def event_participants(request, event_id):
    """Список зарегистрированных участников мероприятия"""
    try:
        event = Event.objects.get(id=event_id)
        registrations = EventRegistration.objects.filter(
            event=event,
            status__in=['registered', 'confirmed']
        ).select_related('athlete', 'athlete__user', 'athlete__main_sport')
        
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response({
            "participants": serializer.data,
            "total_count": registrations.count()
        })
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)


# === Создание мероприятия (директор / горкомспорт) ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    """Создание нового мероприятия"""
    serializer = EventCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        event = serializer.save()
        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# === Загрузка результатов мероприятия ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_event_results(request, event_id):
    """Загрузка результатов мероприятия"""
    try:
        event = Event.objects.get(id=event_id)
        # Здесь должна быть логика загрузки результатов
        return Response({"message": "Результаты загружены"})
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)


# === Получение доступных спортсменов для регистрации (тренер/директор) ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_athletes_for_event(request, event_id):
    """Получить список доступных спортсменов для регистрации на мероприятие"""
    try:
        event = Event.objects.get(id=event_id)
        
        # Получаем возрастные группы мероприятия
        age_groups = event.age_groups.all()
        if not age_groups.exists():
            return Response({"error": "У мероприятия не указаны возрастные группы"}, status=400)
        
        # Определяем, кто может регистрировать
        user = request.user
        athletes = []
        
        if hasattr(user, 'coach_profile'):
            # Тренер - спортсмены из его групп
            from apps.coaches.models import TrainingGroup
            groups = TrainingGroup.objects.filter(coach=user.coach_profile)
            for group in groups:
                enrollments = group.enrollments.filter(status='active')
                for enrollment in enrollments:
                    athlete = enrollment.athlete
                    if athlete not in [a['athlete'] for a in athletes]:
                        # Проверяем возраст
                        if athlete.user.birth_date:
                            age = timezone.now().year - athlete.user.birth_date.year
                            if timezone.now().month < athlete.user.birth_date.month or \
                               (timezone.now().month == athlete.user.birth_date.month and timezone.now().day < athlete.user.birth_date.day):
                                age -= 1
                            
                            eligible = age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
                            
                            already_registered = EventRegistration.objects.filter(
                                event=event,
                                athlete=athlete,
                                status__in=['registered', 'confirmed']
                            ).exists()
                            
                            athletes.append({
                                'id': athlete.id,
                                'full_name': athlete.user.get_full_name(),
                                'age': age,
                                'main_sport': athlete.main_sport.name if athlete.main_sport else None,
                                'eligible': eligible,
                                'already_registered': already_registered
                            })
        
        elif hasattr(user, 'director_role'):
            # Директор - все спортсмены из его организаций
            from apps.organizations.models import Organization
            organizations = Organization.objects.filter(director=user.director_role)
            for org in organizations:
                groups = org.groups.all()
                for group in groups:
                    enrollments = group.enrollments.filter(status='active')
                    for enrollment in enrollments:
                        athlete = enrollment.athlete
                        if athlete not in [a['athlete'] for a in athletes]:
                            # Проверяем возраст
                            if athlete.user.birth_date:
                                age = timezone.now().year - athlete.user.birth_date.year
                                if timezone.now().month < athlete.user.birth_date.month or \
                                   (timezone.now().month == athlete.user.birth_date.month and timezone.now().day < athlete.user.birth_date.day):
                                    age -= 1
                                
                                eligible = age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
                                
                                already_registered = EventRegistration.objects.filter(
                                    event=event,
                                    athlete=athlete,
                                    status__in=['registered', 'confirmed']
                                ).exists()
                                
                                athletes.append({
                                    'id': athlete.id,
                                    'full_name': athlete.user.get_full_name(),
                                    'age': age,
                                    'main_sport': athlete.main_sport.name if athlete.main_sport else None,
                                    'eligible': eligible,
                                    'already_registered': already_registered
                                })
        
        return Response({"athletes": athletes})
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


# === Получение доступных групп для регистрации (тренер/директор) ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_groups_for_event(request, event_id):
    """Получить список доступных групп для регистрации на мероприятие"""
    try:
        event = Event.objects.get(id=event_id)
        user = request.user
        groups = []
        
        if hasattr(user, 'coach_profile'):
            from apps.coaches.models import TrainingGroup
            coach_groups = TrainingGroup.objects.filter(coach=user.coach_profile)
            for group in coach_groups:
                athletes_count = group.enrollments.filter(status='active').count()
                groups.append({
                    'id': group.id,
                    'name': group.name,
                    'sport_name': group.sport.name if group.sport else None,
                    'age_level': group.age_level or None,
                    'athletes_count': athletes_count
                })
        
        elif hasattr(user, 'director_role'):
            from apps.organizations.models import Organization
            organizations = Organization.objects.filter(director=user.director_role)
            for org in organizations:
                org_groups = org.groups.all()
                for group in org_groups:
                    athletes_count = group.enrollments.filter(status='active').count()
                    groups.append({
                        'id': group.id,
                        'name': group.name,
                        'sport_name': group.sport.name if group.sport else None,
                        'age_level': group.age_level or None,
                        'athletes_count': athletes_count
                    })
        
        return Response({"groups": groups})
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


# === Массовая регистрация спортсменов/групп (тренер/директор) ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_register_for_event(request, event_id):
    """Массовая регистрация спортсменов или групп на мероприятие"""
    try:
        event = Event.objects.get(id=event_id)
        athlete_ids = request.data.get('athletes', [])
        group_ids = request.data.get('groups', [])
        
        registered_count = 0
        errors = []
        
        # Регистрация отдельных спортсменов
        for athlete_id in athlete_ids:
            try:
                from apps.athletes.models import AthleteProfile
                athlete = AthleteProfile.objects.get(id=athlete_id)
                
                # Проверка возраста
                if athlete.user.birth_date:
                    age = timezone.now().year - athlete.user.birth_date.year
                    if timezone.now().month < athlete.user.birth_date.month or \
                       (timezone.now().month == athlete.user.birth_date.month and timezone.now().day < athlete.user.birth_date.day):
                        age -= 1
                    
                    eligible = event.age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
                    if not eligible:
                        errors.append(f"{athlete.user.get_full_name()}: возраст не соответствует требованиям")
                        continue
                
                registration, created = EventRegistration.objects.get_or_create(
                    event=event,
                    athlete=athlete,
                    defaults={'status': 'registered'}
                )
                if created:
                    registered_count += 1
            except Exception as e:
                errors.append(f"Ошибка регистрации спортсмена {athlete_id}: {str(e)}")
        
        # Регистрация групп
        for group_id in group_ids:
            try:
                from apps.coaches.models import TrainingGroup
                group = TrainingGroup.objects.get(id=group_id)
                enrollments = group.enrollments.filter(status='active')
                
                for enrollment in enrollments:
                    athlete = enrollment.athlete
                    try:
                        # Проверка возраста
                        if athlete.user.birth_date:
                            age = timezone.now().year - athlete.user.birth_date.year
                            if timezone.now().month < athlete.user.birth_date.month or \
                               (timezone.now().month == athlete.user.birth_date.month and timezone.now().day < athlete.user.birth_date.day):
                                age -= 1
                            
                            eligible = event.age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
                            if not eligible:
                                continue
                        
                        registration, created = EventRegistration.objects.get_or_create(
                            event=event,
                            athlete=athlete,
                            defaults={'status': 'registered'}
                        )
                        if created:
                            registered_count += 1
                    except Exception:
                        continue
            except Exception as e:
                errors.append(f"Ошибка регистрации группы {group_id}: {str(e)}")
        
        return Response({
            "registered_count": registered_count,
            "errors": errors if errors else None
        })
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)
