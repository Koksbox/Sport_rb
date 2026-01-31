# apps/athletes/api/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import AthleteProfileSerializer, ParentRequestSerializer, ClubForAthleteSerializer, \
    EnrollmentRequestSerializer, SectionEnrollmentRequestSerializer
from ...notifications.models import Notification
from ...organizations.models import Organization
from ...parents.models import ParentChildLink


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def get_athlete_profile(request):
    """Получить или обновить профиль спортсмена"""
    try:
        profile = request.user.athlete_profile
        user = request.user
        
        if request.method == 'GET':
            # Возвращаем данные пользователя и профиля
            from apps.users.api.serializers import UserBasicSerializer
            user_serializer = UserBasicSerializer(user, context={'request': request})
            profile_serializer = AthleteProfileSerializer(profile)
            
            data = user_serializer.data
            data.update(profile_serializer.data)
            return Response(data)
        
        elif request.method == 'PATCH':
            # Обновляем данные пользователя
            from apps.users.api.serializers import UserBasicSerializer
            user_data = {}
            profile_data = {}
            
            # Общие данные пользователя (ФИО, фото, дата рождения, пол, город) 
            # редактируются отдельно через /api/users/basic-data/
            # Здесь обрабатываем только специфичные для спортсмена поля
            
            # Остальные данные идут в профиль
            for key, value in request.data.items():
                if key not in user_fields and key != 'csrfmiddlewaretoken':
                    profile_data[key] = value
            
            # Обновляем пользователя
            if user_data:
                user_serializer = UserBasicSerializer(user, data=user_data, partial=True, context={'request': request})
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    return Response(user_serializer.errors, status=400)
            
            # Обновляем профиль
            if profile_data:
                import json
                
                # Обрабатываем дополнительные виды спорта отдельно
                additional_sports = None
                if 'additional_sports' in profile_data:
                    try:
                        # Может быть JSON строка или список
                        if isinstance(profile_data['additional_sports'], str):
                            additional_sports = json.loads(profile_data['additional_sports'])
                        else:
                            additional_sports = profile_data['additional_sports']
                    except:
                        additional_sports = []
                    profile_data.pop('additional_sports')
                
                # Обрабатываем medical_info
                medical_info_data = None
                if 'medical_info' in profile_data:
                    try:
                        if isinstance(profile_data['medical_info'], str):
                            medical_info_data = json.loads(profile_data['medical_info'])
                        else:
                            medical_info_data = profile_data['medical_info']
                    except:
                        medical_info_data = None
                    profile_data.pop('medical_info')
                
                # Обрабатываем goals
                if 'goals' in profile_data:
                    try:
                        if isinstance(profile_data['goals'], str):
                            profile_data['goals'] = json.loads(profile_data['goals'])
                    except:
                        profile_data['goals'] = []
                
                profile_serializer = AthleteProfileSerializer(profile, data=profile_data, partial=True)
                if profile_serializer.is_valid():
                    profile_serializer.save()
                    
                    # Обновляем медицинскую информацию
                    if medical_info_data:
                        from apps.athletes.models import MedicalInfo
                        MedicalInfo.objects.update_or_create(
                            athlete=profile,
                            defaults=medical_info_data
                        )
                    
                    # Обновляем дополнительные виды спорта
                    if additional_sports is not None:
                        from apps.athletes.models import AthleteSpecialization
                        from apps.sports.models import Sport
                        
                        # Удаляем старые дополнительные виды спорта
                        AthleteSpecialization.objects.filter(
                            athlete=profile, 
                            is_primary=False
                        ).delete()
                        
                        # Добавляем новые
                        for sport_id in additional_sports:
                            try:
                                sport = Sport.objects.get(id=sport_id)
                                # Проверяем, что это не основной вид спорта
                                if sport.id != profile.main_sport.id:
                                    AthleteSpecialization.objects.create(
                                        athlete=profile,
                                        sport=sport,
                                        is_primary=False
                                    )
                            except Sport.DoesNotExist:
                                pass
                else:
                    return Response(profile_serializer.errors, status=400)
            
            # Возвращаем обновленные данные
            user_serializer = UserBasicSerializer(user, context={'request': request})
            profile_serializer = AthleteProfileSerializer(profile)
            data = user_serializer.data
            data.update(profile_serializer.data)
            return Response(data)
            
    except Exception as e:
        return Response({"error": "Профиль спортсмена не найден", "detail": str(e)}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parent_requests(request):
    """Список неподтверждённых запросов от родителей"""
    requests = ParentChildLink.objects.filter(
        child_profile__user=request.user,
        is_confirmed=False
    )
    serializer = ParentRequestSerializer(requests, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_parent_request(request, request_id):
    """Подтвердить запрос от родителя"""
    try:
        link = ParentChildLink.objects.get(
            id=request_id,
            child_profile__user=request.user,
            is_confirmed=False
        )
        link.is_confirmed = True
        link.save()

        # Уведомление родителю
        Notification.objects.create(
            recipient=link.parent,
            notification_type='child_linked',
            title='Ребёнок подтвердил связь',
            body=f'Теперь вы можете видеть профиль {link.child_profile.user.first_name}.'
        )

        return Response({"message": "Связь подтверждена."})
    except ParentChildLink.DoesNotExist:
        return Response({"error": "Запрос не найден."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_parent_request(request, request_id):
    """Отклонить запрос от родителя"""
    try:
        link = ParentChildLink.objects.get(
            id=request_id,
            child_profile__user=request.user,
            is_confirmed=False
        )
        link.delete()  # или пометить как отклонённый — по желанию

        Notification.objects.create(
            recipient=link.parent,
            notification_type='child_rejected',
            title='Ребёнок отклонил запрос',
            body='Ваш запрос на привязку не был принят.'
        )

        return Response({"message": "Запрос отклонён."})
    except ParentChildLink.DoesNotExist:
        return Response({"error": "Запрос не найден."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_clubs_for_athlete(request):
    """Поиск клубов для спортсмена"""
    queryset = Organization.objects.filter(status='approved')

    name = request.query_params.get('name')
    city = request.query_params.get('city')
    sport_id = request.query_params.get('sport_id')

    if name:
        queryset = queryset.filter(name__icontains=name)
    if city:
        queryset = queryset.filter(city__name__icontains=city)
    if sport_id:
        queryset = queryset.filter(sport_directions__sport_id=sport_id)

    serializer = ClubForAthleteSerializer(queryset.distinct(), many=True)
    return Response(serializer.data)


# apps/athletes/api/views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_enrollment(request):
    """Отправить заявку на вступление в группу"""
    serializer = EnrollmentRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        enrollment = serializer.save()
        # Уведомление директору организации
        from apps.notifications.models import Notification
        organization = enrollment.group.organization
        if hasattr(organization, 'director'):
            Notification.objects.create(
                recipient=organization.director.user,
                notification_type='athlete_group_request',
                title='Новая заявка на вступление в группу',
                body=f'Спортсмен {enrollment.athlete.user.get_full_name()} хочет вступить в группу "{enrollment.group.name}" в вашей организации.'
            )
        # Уведомление тренерам группы
        coach_memberships = enrollment.group.coach_memberships.filter(status='active')
        for membership in coach_memberships:
            Notification.objects.create(
                recipient=membership.coach.user,
                notification_type='athlete_request',
                title='Новая заявка на вступление',
                body=f'Спортсмен {enrollment.athlete.user.first_name} хочет вступить в вашу группу "{enrollment.group.name}".'
            )
        return Response({"message": "Заявка отправлена. Ожидайте подтверждения."}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_section_enrollment(request):
    """Отправить заявку на вступление в секцию (директор решит группу)"""
    serializer = SectionEnrollmentRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        section_request = serializer.save()
        # Уведомление директору организации
        from apps.notifications.models import Notification
        organization = section_request.organization
        if hasattr(organization, 'director'):
            Notification.objects.create(
                recipient=organization.director.user,
                notification_type='athlete_section_request',
                title='Новая заявка на вступление в секцию',
                body=f'Спортсмен {section_request.athlete.user.get_full_name()} хочет вступить в секцию "{section_request.sport_direction.sport.name}" в вашей организации. Определите группу для спортсмена.'
            )
        return Response({"message": "Заявка отправлена. Директор решит, в какую группу вас определить."}, status=201)
    return Response(serializer.errors, status=400)


# apps/athletes/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .serializers import AttendanceProgressSerializer, EventProgressSerializer, AchievementProgressSerializer
from apps.attendance.models import AttendanceRecord
from apps.events.models import EventParticipation
from apps.achievements.models import Achievement

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_athlete_progress(request):
    """Прогресс спортсмена за последние 6 месяцев"""
    try:
        athlete = request.user.athlete_profile
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=180)

        # Посещаемость
        attendance = AttendanceRecord.objects.filter(
            athlete=athlete,
            date__range=[start_date, end_date]
        ).order_by('date')

        # Участие в мероприятиях
        events = EventParticipation.objects.filter(
            athlete=athlete,
            event__start_date__range=[start_date, end_date]
        ).select_related('event', 'event__results').order_by('event__start_date')

        # Достижения
        achievements = Achievement.objects.filter(
            athlete=athlete,
            date__range=[start_date, end_date]
        ).order_by('date')

        # Сериализуем данные
        attendance_serializer = AttendanceProgressSerializer(attendance, many=True)
        events_serializer = EventProgressSerializer(events, many=True)
        achievements_serializer = AchievementProgressSerializer(achievements, many=True)

        data = {
            'attendance': attendance_serializer.data,
            'events': events_serializer.data,
            'achievements': achievements_serializer.data
        }

        return Response(data)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Ошибка получения прогресса: {str(e)}', exc_info=True)
        return Response({"error": "Профиль спортсмена не найден"}, status=404)