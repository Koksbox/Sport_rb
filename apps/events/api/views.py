# apps/events/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import (
    EventSerializer, EventCreateSerializer,
    EventRegistrationSerializer, EventResultSerializer
)
from apps.events.models import Event, EventRegistration, EventResult
from apps.athletes.models import AthleteProfile
from apps.training.models import TrainingGroup, Enrollment
from apps.organizations.staff.coach_membership import CoachMembership
from apps.training.models import TrainingGroup, Enrollment
from apps.organizations.staff.coach_membership import CoachMembership


# === Просмотр мероприятий ===
@api_view(['GET'])
@permission_classes([AllowAny])
def list_events(request):
    """Список всех опубликованных мероприятий"""
    events = Event.objects.filter(status='published').order_by('-start_date')

    # Фильтры
    event_type = request.query_params.get('event_type')
    city = request.query_params.get('city')
    sport = request.query_params.get('sport')
    
    if event_type:
        events = events.filter(event_type=event_type)
    if city:
        events = events.filter(city__name__icontains=city)
    if sport:
        # Фильтр по виду спорта через категорию мероприятия
        events = events.filter(category__sport__name__icontains=sport)

    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


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
    try:
        event = Event.objects.get(id=event_id, status='published')
        athlete = request.user.athlete_profile

        # Проверка возраста
        age = timezone.now().year - athlete.user.birth_date.year
        eligible = event.age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
        if not eligible:
            return Response({"error": "Возраст не соответствует требованиям"}, status=400)

        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            athlete=athlete,
            defaults={'status': 'registered'}
        )
        if not created:
            return Response({"error": "Вы уже зарегистрированы"}, status=400)

        return Response({"message": "Регистрация успешна!"})
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception:
        return Response({"error": "Профиль спортсмена не найден"}, status=400)


# === Создание мероприятия (директор / горкомспорт) ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    """Создать мероприятие"""
    # Определяем организатора
    serializer = EventCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        if hasattr(request.user, 'director_role'):
            org = request.user.director_role.organization
            event = serializer.save(organizer_org=org, organizer_user=None)
            return Response(EventSerializer(event).data, status=201)
        elif hasattr(request.user, 'committee_role'):
            event = serializer.save(organizer_user=request.user, organizer_org=None)
            return Response(EventSerializer(event).data, status=201)

    return Response({"error": "Недостаточно прав"}, status=403)


# === Загрузка результатов (тренер / директор) ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_event_results(request, event_id):
    """Загрузить результаты мероприятия"""
    try:
        event = Event.objects.get(id=event_id)
        # Проверка прав: только организатор или тренер из той же организации
        allowed = False
        if event.organizer_org and hasattr(request.user, 'coach_profile'):
            coach = request.user.coach_profile
            if event.organizer_org.coach_memberships.filter(coach=coach).exists():
                allowed = True
        if event.organizer_user == request.user or (event.organizer_org and hasattr(event.organizer_org, 'director') and event.organizer_org.director.user == request.user):
            allowed = True

        if not allowed:
            return Response({"error": "Нет доступа"}, status=403)

        results_data = request.data.get('results', [])
        for res in results_data:
            athlete_id = res.get('athlete')
            try:
                athlete = AthleteProfile.objects.get(id=athlete_id)
                EventResult.objects.update_or_create(
                    event=event,
                    athlete=athlete,
                    defaults={
                        'place': res.get('place'),
                        'result_value': res.get('result_value', ''),
                        'notes': res.get('notes', '')
                    }
                )
                # Автоматически создаём достижение
                from apps.achievements.models import Achievement
                Achievement.objects.get_or_create(
                    athlete=athlete,
                    event=event,
                    defaults={
                        'title': f"Участие в {event.title}",
                        'achievement_type': 'competition',
                        'date': event.start_date
                    }
                )
            except AthleteProfile.DoesNotExist:
                continue

        return Response({"message": "Результаты загружены"})
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)


# === Получение спортсменов/групп для тренера и директора ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_athletes_for_event(request, event_id):
    """Получить список доступных спортсменов для регистрации на мероприятие (тренер/директор)"""
    try:
        event = Event.objects.get(id=event_id)
        athletes_list = []
        
        # Проверяем роль
        is_coach = hasattr(request.user, 'coach_profile')
        is_director = hasattr(request.user, 'director_role')
        
        if is_coach:
            # Тренер видит только спортсменов из своих групп
            coach = request.user.coach_profile
            memberships = CoachMembership.objects.filter(
                coach=coach, 
                status='active'
            ).prefetch_related('groups', 'groups__enrollments', 'groups__enrollments__athlete', 'groups__enrollments__athlete__user')
            
            athlete_ids = set()
            for membership in memberships:
                for group in membership.groups.all():
                    enrollments = group.enrollments.filter(status='active')
                    for enrollment in enrollments:
                        athlete_ids.add(enrollment.athlete.id)
            
            athletes = AthleteProfile.objects.filter(id__in=athlete_ids).select_related('user', 'main_sport')
            
        elif is_director:
            # Директор видит всех спортсменов из своей организации
            director = request.user.director_role
            organization = director.organization
            
            # Получаем всех спортсменов из групп организации
            groups = TrainingGroup.objects.filter(organization=organization, is_active=True)
            enrollments = Enrollment.objects.filter(
                group__in=groups,
                status='active'
            ).select_related('athlete', 'athlete__user', 'athlete__main_sport')
            
            athlete_ids = set(e.athlete.id for e in enrollments)
            athletes = AthleteProfile.objects.filter(id__in=athlete_ids).select_related('user', 'main_sport')
        else:
            return Response({"error": "Только тренер или директор могут регистрировать спортсменов"}, status=403)
        
        # Фильтруем по возрасту мероприятия
        athletes_data = []
        for athlete in athletes:
            age = timezone.now().year - athlete.user.birth_date.year
            eligible = event.age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
            
            # Проверяем, не зарегистрирован ли уже
            already_registered = EventRegistration.objects.filter(
                event=event,
                athlete=athlete
            ).exists()
            
            athletes_data.append({
                'id': athlete.id,
                'full_name': athlete.user.get_full_name(),
                'birth_date': athlete.user.birth_date.isoformat() if athlete.user.birth_date else None,
                'age': age,
                'main_sport': athlete.main_sport.name if athlete.main_sport else None,
                'eligible': eligible,
                'already_registered': already_registered
            })
        
        return Response({'athletes': athletes_data})
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_groups_for_event(request, event_id):
    """Получить список доступных групп для регистрации на мероприятие (тренер/директор)"""
    try:
        event = Event.objects.get(id=event_id)
        groups_list = []
        
        # Проверяем роль
        is_coach = hasattr(request.user, 'coach_profile')
        is_director = hasattr(request.user, 'director_role')
        
        if is_coach:
            # Тренер видит только свои группы
            coach = request.user.coach_profile
            memberships = CoachMembership.objects.filter(
                coach=coach, 
                status='active'
            ).prefetch_related('groups', 'groups__enrollments')
            
            group_ids = set()
            for membership in memberships:
                for group in membership.groups.all():
                    group_ids.add(group.id)
            
            groups = TrainingGroup.objects.filter(
                id__in=group_ids,
                is_active=True
            ).select_related('sport', 'age_level', 'organization')
            
        elif is_director:
            # Директор видит все группы своей организации
            director = request.user.director_role
            organization = director.organization
            
            groups = TrainingGroup.objects.filter(
                organization=organization,
                is_active=True
            ).select_related('sport', 'age_level', 'organization')
        else:
            return Response({"error": "Только тренер или директор могут регистрировать группы"}, status=403)
        
        groups_data = []
        for group in groups:
            # Подсчитываем количество спортсменов в группе
            enrollments = group.enrollments.filter(status='active')
            athletes_count = enrollments.count()
            
            groups_data.append({
                'id': group.id,
                'name': group.name,
                'sport_name': group.sport.name if group.sport else None,
                'age_level': group.age_level.name if group.age_level else None,
                'organization_name': group.organization.name,
                'athletes_count': athletes_count
            })
        
        return Response({'groups': groups_data})
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


# === Массовая регистрация на мероприятие ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_register_for_event(request, event_id):
    """Массовая регистрация спортсменов или групп на мероприятие (тренер/директор)"""
    try:
        event = Event.objects.get(id=event_id, status='published')
        
        # Проверяем роль
        is_coach = hasattr(request.user, 'coach_profile')
        is_director = hasattr(request.user, 'director_role')
        
        if not (is_coach or is_director):
            return Response({"error": "Только тренер или директор могут регистрировать спортсменов"}, status=403)
        
        athlete_ids = request.data.get('athletes', [])
        group_ids = request.data.get('groups', [])
        
        if not athlete_ids and not group_ids:
            return Response({"error": "Укажите спортсменов или группы для регистрации"}, status=400)
        
        registered_count = 0
        skipped_count = 0
        errors = []
        
        # Регистрация отдельных спортсменов
        if athlete_ids:
            for athlete_id in athlete_ids:
                try:
                    athlete = AthleteProfile.objects.get(id=athlete_id)
                    
                    # Проверка доступа
                    if is_coach:
                        coach = request.user.coach_profile
                        # Проверяем, что спортсмен в группе тренера
                        memberships = CoachMembership.objects.filter(
                            coach=coach, status='active'
                        ).prefetch_related('groups', 'groups__enrollments')
                        has_access = False
                        for membership in memberships:
                            for group in membership.groups.all():
                                if group.enrollments.filter(athlete=athlete, status='active').exists():
                                    has_access = True
                                    break
                            if has_access:
                                break
                        if not has_access:
                            errors.append(f"Нет доступа к спортсмену {athlete.user.get_full_name()}")
                            skipped_count += 1
                            continue
                    
                    elif is_director:
                        director = request.user.director_role
                        organization = director.organization
                        # Проверяем, что спортсмен в группе организации
                        has_access = Enrollment.objects.filter(
                            athlete=athlete,
                            group__organization=organization,
                            status='active'
                        ).exists()
                        if not has_access:
                            errors.append(f"Спортсмен {athlete.user.get_full_name()} не в вашей организации")
                            skipped_count += 1
                            continue
                    
                    # Проверка возраста
                    age = timezone.now().year - athlete.user.birth_date.year
                    eligible = event.age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
                    if not eligible:
                        errors.append(f"Возраст спортсмена {athlete.user.get_full_name()} не соответствует требованиям")
                        skipped_count += 1
                        continue
                    
                    # Регистрация
                    registration, created = EventRegistration.objects.get_or_create(
                        event=event,
                        athlete=athlete,
                        defaults={'status': 'registered'}
                    )
                    if created:
                        registered_count += 1
                    else:
                        skipped_count += 1
                        errors.append(f"Спортсмен {athlete.user.get_full_name()} уже зарегистрирован")
                except AthleteProfile.DoesNotExist:
                    errors.append(f"Спортсмен с ID {athlete_id} не найден")
                    skipped_count += 1
        
        # Регистрация групп
        if group_ids:
            for group_id in group_ids:
                try:
                    group = TrainingGroup.objects.get(id=group_id, is_active=True)
                    
                    # Проверка доступа
                    if is_coach:
                        coach = request.user.coach_profile
                        has_access = CoachMembership.objects.filter(
                            coach=coach,
                            groups=group,
                            status='active'
                        ).exists()
                        if not has_access:
                            errors.append(f"Нет доступа к группе {group.name}")
                            skipped_count += 1
                            continue
                    
                    elif is_director:
                        director = request.user.director_role
                        organization = director.organization
                        if group.organization != organization:
                            errors.append(f"Группа {group.name} не в вашей организации")
                            skipped_count += 1
                            continue
                    
                    # Регистрируем всех спортсменов группы
                    enrollments = group.enrollments.filter(status='active')
                    for enrollment in enrollments:
                        athlete = enrollment.athlete
                        
                        # Проверка возраста
                        age = timezone.now().year - athlete.user.birth_date.year
                        eligible = event.age_groups.filter(min_age__lte=age, max_age__gte=age).exists()
                        if not eligible:
                            continue
                        
                        # Регистрация
                        registration, created = EventRegistration.objects.get_or_create(
                            event=event,
                            athlete=athlete,
                            defaults={'status': 'registered'}
                        )
                        if created:
                            registered_count += 1
                        # Если уже зарегистрирован, просто пропускаем
                        
                except TrainingGroup.DoesNotExist:
                    errors.append(f"Группа с ID {group_id} не найдена")
                    skipped_count += 1
        
        response_data = {
            "message": f"Зарегистрировано: {registered_count}, пропущено: {skipped_count}",
            "registered_count": registered_count,
            "skipped_count": skipped_count
        }
        
        if errors:
            response_data["errors"] = errors[:10]  # Ограничиваем количество ошибок
        
        return Response(response_data, status=200 if registered_count > 0 else 400)
        
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)