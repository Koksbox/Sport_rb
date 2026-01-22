# apps/parents/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChildLinkRequestSerializer, ChildProfileSerializer
from apps.parents.models import ParentChildLink
from apps.attendance.models import AttendanceRecord
from apps.events.models import EventRegistration

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_child_link(request):
    """Родитель отправляет запрос на привязку ребёнка по уникальному ID роли"""
    serializer = ChildLinkRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        link = serializer.save()
        if link.status == 'confirmed':
            return Response({"message": "Ребёнок уже привязан."}, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Запрос на привязку отправлен. Ожидайте подтверждения от ребёнка.",
                "status": link.status
            }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_children_list(request):
    """Список всех подтверждённых детей"""
    links = ParentChildLink.objects.filter(
        parent=request.user, 
        status='confirmed'
    ).select_related('child_profile__user', 'child_profile__main_sport', 'child_profile__city')
    children = [link.child_profile for link in links]
    serializer = ChildProfileSerializer(children, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_child_profile(request, child_id):
    """Просмотр профиля конкретного ребёнка с подробной статистикой"""
    try:
        link = ParentChildLink.objects.get(
            parent=request.user,
            child_profile_id=child_id,
            status='confirmed'
        )
        child = link.child_profile
        
        # Получаем базовую информацию
        serializer = ChildProfileSerializer(child)
        data = serializer.data
        
        # Добавляем статистику посещаемости
        attendance_records = AttendanceRecord.objects.filter(
            athlete=child
        ).select_related('group', 'session')
        
        total_sessions = attendance_records.count()
        attended_sessions = attendance_records.filter(attended=True).count()
        attendance_rate = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        data['attendance_stats'] = {
            'total_sessions': total_sessions,
            'attended_sessions': attended_sessions,
            'attendance_rate': round(attendance_rate, 2)
        }
        
        # Добавляем информацию о мероприятиях
        event_registrations = EventRegistration.objects.filter(
            athlete=child
        ).select_related('event')
        
        data['events'] = [{
            'id': reg.event.id,
            'title': reg.event.title or reg.event.name,
            'date': reg.event.start_date,
            'status': reg.status
        } for reg in event_registrations]
        
        return Response(data)
    except ParentChildLink.DoesNotExist:
        return Response({"error": "Ребёнок не найден или не подтверждён."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_requests(request):
    """Получить список ожидающих подтверждения заявок"""
    # Заявки, где текущий пользователь - родитель
    parent_requests = ParentChildLink.objects.filter(
        parent=request.user,
        status__in=['pending_child', 'pending_parent']
    ).select_related('child_profile__user')
    
    # Заявки, где текущий пользователь - ребёнок
    child_requests = ParentChildLink.objects.filter(
        child_profile__user=request.user,
        status__in=['pending_child', 'pending_parent']
    ).select_related('parent')
    
    results = {
        'as_parent': [{
            'id': link.id,
            'child_name': link.child_profile.user.get_full_name(),
            'status': link.status,
            'requested_by': link.requested_by
        } for link in parent_requests],
        'as_child': [{
            'id': link.id,
            'parent_name': link.parent.get_full_name(),
            'status': link.status,
            'requested_by': link.requested_by
        } for link in child_requests]
    }
    
    return Response(results)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_link(request, link_id):
    """Подтвердить заявку на связь родитель-ребёнок"""
    try:
        # Проверяем, может ли пользователь подтвердить эту заявку
        link = ParentChildLink.objects.get(id=link_id)
        
        # Если пользователь - родитель и заявка ожидает подтверждения от родителя
        if link.parent == request.user and link.status == 'pending_parent':
            link.status = 'confirmed'
            link.save()
            return Response({"message": "Заявка подтверждена."})
        
        # Если пользователь - ребёнок и заявка ожидает подтверждения от ребёнка
        if link.child_profile.user == request.user and link.status == 'pending_child':
            link.status = 'confirmed'
            link.save()
            return Response({"message": "Заявка подтверждена."})
        
        return Response({"error": "Вы не можете подтвердить эту заявку."}, status=status.HTTP_403_FORBIDDEN)
    except ParentChildLink.DoesNotExist:
        return Response({"error": "Заявка не найдена."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_link(request, link_id):
    """Отклонить заявку на связь родитель-ребёнок"""
    try:
        link = ParentChildLink.objects.get(id=link_id)
        
        # Проверяем права
        if link.parent == request.user or link.child_profile.user == request.user:
            link.status = 'rejected'
            link.save()
            return Response({"message": "Заявка отклонена."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Вы не можете отклонить эту заявку."}, status=status.HTTP_403_FORBIDDEN)
    except ParentChildLink.DoesNotExist:
        return Response({"error": "Заявка не найдена."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_role_id(request):
    """Получить уникальный ID текущей активной роли пользователя"""
    active_role_name = request.session.get('active_role')
    if not active_role_name:
        # Если активная роль не установлена, пытаемся найти роль спортсмена
        try:
            user_role = request.user.roles.get(role='athlete', is_active=True)
        except request.user.roles.model.DoesNotExist:
            return Response({"error": "Активная роль не установлена"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            user_role = request.user.roles.get(role=active_role_name, is_active=True)
        except request.user.roles.model.DoesNotExist:
            return Response({"error": "Роль не найдена"}, status=status.HTTP_404_NOT_FOUND)
    
    # Генерируем unique_id, если его нет
    if not user_role.unique_id:
        import random
        import string
        while True:
            unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not request.user.roles.model.objects.filter(unique_id=unique_id).exists():
                user_role.unique_id = unique_id
                user_role.save()
                break
    
    return Response({
        "role": user_role.role,
        "unique_id": user_role.unique_id,
        "role_name": dict(request.user.roles.model.ROLE_CHOICES).get(user_role.role, user_role.role)
    })