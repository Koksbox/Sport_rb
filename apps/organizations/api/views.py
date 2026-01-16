# apps/organizations/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import UserRole
from .serializers import OrganizationModerationSerializer
from apps.organizations.services.moderation import approve_organization
from apps.organizations.models import Organization


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def moderate_organization(request, org_id):
    # Проверка: только admin_rb может модерировать
    if not request.user.roles.filter(role='admin_rb').exists():
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

    try:
        org = Organization.objects.get(id=org_id, status='pending')
    except Organization.DoesNotExist:
        return Response({"error": "Организация не найдена или уже обработана"}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrganizationModerationSerializer(org, data=request.data, partial=True)
    if serializer.is_valid():
        org = serializer.save()
        if org.status == 'approved':
            approve_organization(org, request.user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# apps/organizations/api/views.py
from apps.coaches.models import ClubRequest
from apps.coaches.models import CoachProfile
from apps.organizations.staff.coach_membership import CoachMembership

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_coach_request(request, request_id):
    try:
        club_request = ClubRequest.objects.get(
            id=request_id,
            organization__director__user=request.user,
            status='pending'
        )
        club_request.status = 'approved'
        club_request.save()

        # Создаём профиль тренера, если ещё нет
        coach, _ = CoachProfile.objects.get_or_create(
            user=club_request.coach.user,
            defaults={
                'city': request.user.city,
                'specialization': club_request.specialization,
                'experience_years': 0
            }
        )

        # Назначаем роль
        from apps.users.models import UserRole
        UserRole.objects.get_or_create(user=coach.user, role='coach')

        # Добавляем в штат клуба
        membership, _ = CoachMembership.objects.get_or_create(
            coach=coach,
            organization=club_request.organization,
            defaults={'status': 'active'}
        )

        return Response({"message": "Тренер одобрен и добавлен в клуб."})
    except ClubRequest.DoesNotExist:
        return Response({"error": "Заявка не найдена"}, status=404)


# apps/organizations/api/views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_coach_request(request, request_id):
    try:
        club_request = ClubRequest.objects.get(
            id=request_id,
            organization__director__user=request.user,
            status='pending'
        )
        club_request.status = 'approved'
        club_request.save()

        coach = club_request.coach
        org = club_request.organization

        # Назначаем роль
        UserRole.objects.get_or_create(user=coach.user, role='coach')

        # Создаём запись в штате
        membership, _ = CoachMembership.objects.get_or_create(
            coach=coach,
            organization=org,
            defaults={'status': 'active'}
        )

        # Привязываем возрастные группы
        membership.groups.set(club_request.age_levels.values_list('traininggroup', flat=True))

        return Response({"message": "Тренер одобрен и добавлен в клуб."})
    except ClubRequest.DoesNotExist:
        return Response({"error": "Заявка не найдена"}, status=404)