# apps/organizations/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    OrganizationCreateSerializer,
    OrganizationModerationSerializer
)
from apps.organizations.models import Organization
from apps.organizations.services.moderation import approve_organization
from apps.coaches.models import ClubRequest, CoachProfile
from apps.organizations.staff.coach_membership import CoachMembership

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    """Создать организацию (черновик)"""
    if not request.user.roles.filter(role='organization').exists():
        return Response(
            {"error": "Сначала выберите роль 'organization'"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = OrganizationCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        org = serializer.save()
        return Response(
            {"message": "Организация создана. Ожидает модерации."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def moderate_organization(request, org_id):
    if not request.user.roles.filter(role='admin_rb').exists():
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

    try:
        org = Organization.objects.get(id=org_id, status='pending')
    except Organization.DoesNotExist:
        return Response({"error": "Организация не найдена"}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrganizationModerationSerializer(org, data=request.data, partial=True)
    if serializer.is_valid():
        org = serializer.save()
        if org.status == 'approved':
            approve_organization(org, request.user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        from apps.users.models import UserRole
        UserRole.objects.get_or_create(user=coach.user, role='coach')

        membership, _ = CoachMembership.objects.get_or_create(
            coach=coach,
            organization=org,
            defaults={'status': 'active'}
        )

        return Response({"message": "Тренер одобрен и добавлен в клуб."})
    except ClubRequest.DoesNotExist:
        return Response({"error": "Заявка не найдена"}, status=404)