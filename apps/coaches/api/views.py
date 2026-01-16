# apps/coaches/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import TrainingGroupSerializer, ClubSearchSerializer, ClubRequestSerializer
from apps.training.models import Enrollment
from apps.notifications.models import Notification
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coach_groups(request):
    """Список всех групп тренера (активных и архивных)"""
    try:
        coach = request.user.coach_profile
        memberships = coach.coach_memberships.filter(status='active')
        groups = []
        for membership in memberships:
            groups.extend(membership.groups.all())

        serializer = TrainingGroupSerializer(groups, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception:
        return Response({"error": "Профиль тренера не найден"}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_athlete_enrollment(request, enrollment_id):
    """Одобрить заявку спортсмена на вступление в группу"""
    try:
        enrollment = Enrollment.objects.get(
            id=enrollment_id,
            status='pending'
        )
        # Проверка: группа принадлежит тренеру
        coach = request.user.coach_profile
        if not enrollment.group.coach_memberships.filter(
                coach=coach, status='active'
        ).exists():
            return Response({"error": "Нет доступа к этой группе"}, status=403)

        enrollment.status = 'active'
        enrollment.joined_at = timezone.now()
        enrollment.save()

        # Уведомление родителям и самому спортсмену
        athlete = enrollment.athlete
        Notification.objects.create(
            recipient=athlete.user,
            notification_type='enrollment_approved',
            title='Вы зачислены в группу',
            body=f'Тренер одобрил ваше вступление в группу "{enrollment.group.name}".'
        )

        # Уведомление: ознакомьтесь с мед. данными
        Notification.objects.create(
            recipient=request.user,
            notification_type='medical_review',
            title='Ознакомьтесь с медицинскими данными ученика',
            body=f'Спортсмен {athlete.user.first_name} зачислен в вашу группу. Проверьте медицинские данные.'
        )

        return Response({"message": "Заявка одобрена."})
    except Enrollment.DoesNotExist:
        return Response({"error": "Заявка не найдена"}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_athlete_enrollment(request, enrollment_id):
    """Отклонить заявку спортсмена"""
    try:
        enrollment = Enrollment.objects.get(
            id=enrollment_id,
            status='pending'
        )
        coach = request.user.coach_profile
        if not enrollment.group.coach_memberships.filter(
                coach=coach, status='active'
        ).exists():
            return Response({"error": "Нет доступа к этой группе"}, status=403)

        enrollment.status = 'rejected'
        enrollment.save()

        Notification.objects.create(
            recipient=enrollment.athlete.user,
            notification_type='enrollment_rejected',
            title='Ваша заявка отклонена',
            body=f'Тренер отклонил вашу заявку в группу "{enrollment.group.name}".'
        )

        return Response({"message": "Заявка отклонена."})
    except Enrollment.DoesNotExist:
        return Response({"error": "Заявка не найдена"}, status=404)


# apps/coaches/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.organizations.models import Organization

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_clubs(request):
    """Поиск клубов по названию, городу, виду спорта"""
    queryset = Organization.objects.filter(status='approved')  # только одобренные

    name = request.query_params.get('name')
    city = request.query_params.get('city')
    sport_id = request.query_params.get('sport_id')

    if name:
        queryset = queryset.filter(name__icontains=name)
    if city:
        queryset = queryset.filter(city__name__icontains=city)
    if sport_id:
        queryset = queryset.filter(sport_directions__sport_id=sport_id)

    serializer = ClubSearchSerializer(queryset.distinct(), many=True)
    return Response(serializer.data)


# apps/coaches/api/views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_club_request(request):
    """Отправить заявку на работу в клуб"""
    serializer = ClubRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        request_obj = serializer.save()
        # Уведомление директору
        from apps.notifications.models import Notification
        director = request_obj.organization.director.user
        Notification.objects.create(
            recipient=director,
            notification_type='coach_request',
            title='Новая заявка от тренера',
            body=f'Тренер {request_obj.coach.user.first_name} хочет работать в вашей организации.'
        )
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)