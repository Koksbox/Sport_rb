# apps/admin_rb/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, AssignRoleSerializer
from apps.users.models import UserRole
from apps.organizations.models import Organization

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_organizations(request):
    """Список организаций на модерации"""
    if not request.user.roles.filter(role='admin_rb').exists():
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

    orgs = Organization.objects.filter(status='pending')
    data = []
    for org in orgs:
        data.append({
            'id': org.id,
            'name': org.name,
            'inn': org.inn,
            'created_by': UserSerializer(org.created_by).data
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_role(request):
    """Назначить роль (moderator / admin_rb)"""
    if not request.user.roles.filter(role='admin_rb').exists():
        return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

    serializer = AssignRoleSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": f"Роль назначена пользователю {user.email}"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)