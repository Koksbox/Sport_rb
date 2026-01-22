# apps/organizations/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    OrganizationCreateSerializer,
    OrganizationModerationSerializer,
    OrganizationListSerializer,
    OrganizationDetailSerializer
)
from apps.organizations.models import Organization
from apps.organizations.services.moderation import approve_organization
from apps.coaches.models import ClubRequest, CoachProfile
from apps.organizations.staff.coach_membership import CoachMembership

@api_view(['GET'])
@permission_classes([AllowAny])
def list_organizations(request):
    """Список одобренных организаций"""
    organizations = Organization.objects.filter(status='approved')
    
    # Фильтры
    city = request.query_params.get('city')
    sport = request.query_params.get('sport')
    
    if city:
        organizations = organizations.filter(city__name__icontains=city)
    
    if sport:
        from apps.organizations.models import SportDirection
        organizations = organizations.filter(
            sport_directions__sport__name__icontains=sport
        ).distinct()
    
    serializer = OrganizationListSerializer(organizations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_organizations(request):
    """Получить список организаций пользователя (директор или создатель)"""
    organizations = Organization.objects.filter(
        created_by=request.user
    ) | Organization.objects.filter(
        director__user=request.user
    )
    organizations = organizations.distinct()
    serializer = OrganizationListSerializer(organizations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_organization_detail(request, org_id):
    """Детальная информация об организации"""
    try:
        organization = Organization.objects.get(id=org_id, status='approved')
        serializer = OrganizationDetailSerializer(organization)
        return Response(serializer.data)
    except Organization.DoesNotExist:
        return Response({"error": "Организация не найдена"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    """Создать организацию (черновик)"""
    # Роль 'organization' больше не требуется - создаём автоматически при создании организации

    # Обработка файлов документов
    data = request.data.copy()
    files = request.FILES.getlist('documents')
    
    documents_data = []
    if files:
        for file in files:
            # Определяем тип документа по расширению или используем 'license' по умолчанию
            doc_type = 'license'  # По умолчанию лицензия
            if 'устав' in file.name.lower() or 'charter' in file.name.lower():
                doc_type = 'charter'
            elif 'инн' in file.name.lower() or 'inn' in file.name.lower():
                doc_type = 'inn'
            
            documents_data.append({
                'doc_type': doc_type,
                'file_path': file
            })
    
    if documents_data:
        data['documents'] = documents_data

    serializer = OrganizationCreateSerializer(
        data=data,
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
    # Проверяем роль модератора или админа
    from apps.admin_rb.models import SystemRoleAssignment
    is_moderator = SystemRoleAssignment.objects.filter(
        user=request.user, role='moderator'
    ).exists()
    is_admin = request.user.roles.filter(role='admin_rb').exists()
    
    if not (is_moderator or is_admin):
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