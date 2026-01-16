# apps/parents/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChildLinkRequestSerializer, ChildProfileSerializer
from apps.parents.models import ParentChildLink

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_child_link(request):
    """Родитель отправляет запрос на привязку ребёнка"""
    serializer = ChildLinkRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        link = serializer.save()
        if link.is_confirmed:
            return Response({"message": "Ребёнок уже привязан."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Запрос на привязку отправлен. Ожидайте подтверждения."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_children_list(request):
    """Список всех подтверждённых детей"""
    links = ParentChildLink.objects.filter(parent=request.user, is_confirmed=True)
    children = [link.child_profile for link in links]
    serializer = ChildProfileSerializer(children, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_child_profile(request, child_id):
    """Просмотр профиля конкретного ребёнка"""
    try:
        link = ParentChildLink.objects.get(
            parent=request.user,
            child_profile_id=child_id,
            is_confirmed=True
        )
        serializer = ChildProfileSerializer(link.child_profile)
        return Response(serializer.data)
    except ParentChildLink.DoesNotExist:
        return Response({"error": "Ребёнок не найден или не подтверждён."}, status=status.HTTP_404_NOT_FOUND)