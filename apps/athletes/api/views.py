# apps/athletes/api/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import AthleteProfileSerializer, ParentRequestSerializer, ClubForAthleteSerializer, \
    EnrollmentRequestSerializer
from ...notifications.models import Notification
from ...organizations.models import Organization
from ...parents.models import ParentChildLink


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_athlete_profile(request):
    try:
        profile = request.user.athlete_profile
        serializer = AthleteProfileSerializer(profile)
        return Response(serializer.data)
    except Exception:
        return Response({"error": "Профиль спортсмена не найден"}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_athlete_profile(request):
    try:
        profile = request.user.athlete_profile
        serializer = AthleteProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except Exception:
        return Response({"error": "Профиль спортсмена не найден"}, status=404)


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
        # Уведомление тренерам группы
        from apps.notifications.models import Notification
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