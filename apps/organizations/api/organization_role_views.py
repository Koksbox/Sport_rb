# apps/organizations/api/organization_role_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.organizations.models.organization_role_request import OrganizationRoleRequest
from apps.organizations.api.organization_role_serializers import (
    OrganizationRoleRequestSerializer,
    OrganizationRoleRequestCreateSerializer,
    OrganizationRoleRequestReviewSerializer
)
from apps.users.models import UserRole
from apps.notifications.models import Notification

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization_role_request(request):
    """Создать заявку на роль организации"""
    serializer = OrganizationRoleRequestCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        role_request = serializer.save()
        
        # Отправляем уведомление администраторам
        from apps.users.models import CustomUser
        admins = CustomUser.objects.filter(roles__role='admin_rb', roles__is_active=True).distinct()
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                notification_type='org_role_request',
                title='Новая заявка на роль организации',
                body=f'Пользователь {request.user.get_full_name()} подал заявку на роль организации.'
            )
        
        return Response({
            'message': 'Заявка успешно отправлена. Ожидайте рассмотрения.',
            'request_id': role_request.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_organization_role_request(request):
    """Получить свою заявку на роль организации"""
    try:
        role_request = OrganizationRoleRequest.objects.filter(user=request.user).latest('created_at')
        serializer = OrganizationRoleRequestSerializer(role_request)
        return Response(serializer.data)
    except OrganizationRoleRequest.DoesNotExist:
        return Response({'message': 'Заявка не найдена'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_organization_role_requests(request):
    """Список всех заявок на роль организации (только для администраторов)"""
    # Проверяем права доступа
    is_admin = request.user.roles.filter(role='admin_rb', is_active=True).exists()
    if not is_admin:
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
    
    status_filter = request.query_params.get('status', 'pending')
    requests = OrganizationRoleRequest.objects.filter(status=status_filter).order_by('-created_at')
    
    serializer = OrganizationRoleRequestSerializer(requests, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_organization_role_request(request, request_id):
    """Рассмотреть заявку на роль организации (одобрить/отклонить)"""
    # Проверяем права доступа
    is_admin = request.user.roles.filter(role='admin_rb', is_active=True).exists()
    if not is_admin:
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        role_request = OrganizationRoleRequest.objects.get(id=request_id, status='pending')
    except OrganizationRoleRequest.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrganizationRoleRequestReviewSerializer(data=request.data)
    if serializer.is_valid():
        new_status = serializer.validated_data['status']
        rejection_reason = serializer.validated_data.get('rejection_reason', '')
        
        role_request.status = new_status
        role_request.reviewed_by = request.user
        role_request.reviewed_at = timezone.now()
        
        if new_status == 'approved':
            # Создаём роль организации
            UserRole.objects.get_or_create(
                user=role_request.user,
                role='director',
                defaults={'is_active': True}
            )
            
            # Отправляем уведомление пользователю
            Notification.objects.create(
                recipient=role_request.user,
                notification_type='org_role_approved',
                title='Заявка на роль организации одобрена!',
                body='Ваша заявка на роль организации одобрена. Теперь вы можете создать организацию.'
            )
        else:
            role_request.rejection_reason = rejection_reason
            
            # Отправляем уведомление пользователю
            Notification.objects.create(
                recipient=role_request.user,
                notification_type='org_role_rejected',
                title='Заявка на роль организации отклонена',
                body=f'Ваша заявка отклонена. Причина: {rejection_reason}' if rejection_reason else 'Ваша заявка отклонена.'
            )
        
        role_request.save()
        
        serializer_response = OrganizationRoleRequestSerializer(role_request)
        return Response(serializer_response.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
