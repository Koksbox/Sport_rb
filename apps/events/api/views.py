# apps/events/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import (
    EventSerializer, EventCreateSerializer,
    EventRegistrationSerializer, EventResultSerializer
)
from apps.events.models import Event, EventRegistration, EventResult
from ...athletes.models import AthleteProfile


# === Просмотр мероприятий ===
@api_view(['GET'])
def list_events(request):
    """Список всех опубликованных мероприятий"""
    events = Event.objects.filter(status='published').order_by('-start_date')

    # Фильтры
    event_type = request.query_params.get('event_type')
    city = request.query_params.get('city')
    if event_type:
        events = events.filter(event_type=event_type)
    if city:
        events = events.filter(city__name__icontains=city)

    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['GET'])
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
    if hasattr(request.user, 'director_role'):
        org = request.user.director_role.organization
        serializer = EventCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            event = serializer.save(organization=org, organizer_user=None)
            return Response(EventSerializer(event).data, status=201)
    elif hasattr(request.user, 'committee_role'):
        serializer = EventCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            event = serializer.save(organizer_user=request.user, organization=None)
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
        if event.organization and hasattr(request.user, 'coach_profile'):
            coach = request.user.coach_profile
            if event.organization.coach_memberships.filter(coach=coach).exists():
                allowed = True
        if event.organizer_user == request.user or event.organization.director.user == request.user:
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