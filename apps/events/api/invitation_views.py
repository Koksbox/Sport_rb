# apps/events/api/invitation_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Q
from apps.events.models import Event, EventInvitation, EventRegistration
from apps.athletes.models import AthleteProfile
from apps.coaches.models.coach_profile import CoachProfile
from apps.training.models import TrainingGroup
from apps.organizations.models import Organization
from apps.notifications.models import Notification
from .invitation_serializers import EventInvitationSerializer, EventInvitationCreateSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invitations(request):
    """Создание приглашений на мероприятие"""
    serializer = EventInvitationCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    event_id = data['event_id']
    invitation_type = data['invitation_type']
    
    try:
        event = Event.objects.get(id=event_id, status='published')
    except Event.DoesNotExist:
        return Response({"error": "Мероприятие не найдено"}, status=404)
    
    user = request.user
    created_invitations = []
    errors = []
    
    try:
        with transaction.atomic():
            # Приглашения для отдельных спортсменов
            if data.get('athlete_ids'):
                for athlete_id in data['athlete_ids']:
                    try:
                        athlete = AthleteProfile.objects.get(id=athlete_id)
                        
                        # Проверяем, не отправлено ли уже приглашение
                        existing = EventInvitation.objects.filter(
                            event=event,
                            athlete=athlete,
                            status='pending'
                        ).exists()
                        
                        if existing:
                            errors.append(f"Приглашение для {athlete.user.get_full_name()} уже отправлено")
                            continue
                        
                        invitation = EventInvitation.objects.create(
                            event=event,
                            invitation_type='athlete',
                            athlete=athlete,
                            sent_by=user,
                            message=data.get('message', ''),
                            expires_at=data.get('expires_at')
                        )
                        created_invitations.append(invitation)
                        
                        # Создаём уведомление
                        Notification.objects.create(
                            user=athlete.user,
                            title=f"Приглашение на мероприятие",
                            message=f"Вас пригласили на мероприятие '{event.title}'. Проверьте раздел приглашений.",
                            notification_type='event_invitation',
                            related_object_id=invitation.id
                        )
                    except AthleteProfile.DoesNotExist:
                        errors.append(f"Спортсмен с ID {athlete_id} не найден")
            
            # Приглашения для отдельных тренеров
            if data.get('coach_ids'):
                for coach_id in data['coach_ids']:
                    try:
                        coach = CoachProfile.objects.get(id=coach_id)
                        
                        existing = EventInvitation.objects.filter(
                            event=event,
                            coach=coach,
                            status='pending'
                        ).exists()
                        
                        if existing:
                            errors.append(f"Приглашение для {coach.user.get_full_name()} уже отправлено")
                            continue
                        
                        invitation = EventInvitation.objects.create(
                            event=event,
                            invitation_type='coach',
                            coach=coach,
                            sent_by=user,
                            message=data.get('message', ''),
                            expires_at=data.get('expires_at')
                        )
                        created_invitations.append(invitation)
                        
                        Notification.objects.create(
                            user=coach.user,
                            title=f"Приглашение на мероприятие",
                            message=f"Вас пригласили на мероприятие '{event.title}' в качестве тренера.",
                            notification_type='event_invitation',
                            related_object_id=invitation.id
                        )
                    except CoachProfile.DoesNotExist:
                        errors.append(f"Тренер с ID {coach_id} не найден")
            
            # Массовые приглашения для групп (тренер)
            if data.get('group_ids'):
                for group_id in data['group_ids']:
                    try:
                        group = TrainingGroup.objects.get(id=group_id)
                        
                        # Проверяем права (тренер может приглашать только свои группы)
                        if hasattr(user, 'coach_profile') and group.coach != user.coach_profile:
                            errors.append(f"У вас нет доступа к группе {group.name}")
                            continue
                        
                        # Приглашаем всех активных спортсменов группы
                        enrollments = group.enrollments.filter(status='active')
                        for enrollment in enrollments:
                            athlete = enrollment.athlete
                            
                            existing = EventInvitation.objects.filter(
                                event=event,
                                athlete=athlete,
                                status='pending'
                            ).exists()
                            
                            if existing:
                                continue
                            
                            invitation = EventInvitation.objects.create(
                                event=event,
                                invitation_type='athlete',
                                athlete=athlete,
                                sent_by=user,
                                message=data.get('message', ''),
                                expires_at=data.get('expires_at'),
                                group_id=group_id
                            )
                            created_invitations.append(invitation)
                            
                            Notification.objects.create(
                                user=athlete.user,
                                title=f"Приглашение на мероприятие",
                                message=f"Вас пригласили на мероприятие '{event.title}' из группы {group.name}.",
                                notification_type='event_invitation',
                                related_object_id=invitation.id
                            )
                    except TrainingGroup.DoesNotExist:
                        errors.append(f"Группа с ID {group_id} не найдена")
            
            # Массовые приглашения для всех групп организации (организация)
            if data.get('organization_id'):
                try:
                    org = Organization.objects.get(id=data['organization_id'])
                    
                    # Проверяем права (директор может приглашать только из своей организации)
                    if hasattr(user, 'director_role') and org.director != user.director_role:
                        errors.append(f"У вас нет доступа к организации {org.name}")
                        return Response({"error": "Нет доступа"}, status=403)
                    
                    # Приглашаем всех спортсменов и тренеров организации
                    groups = org.groups.all()
                    for group in groups:
                        enrollments = group.enrollments.filter(status='active')
                        for enrollment in enrollments:
                            athlete = enrollment.athlete
                            
                            existing = EventInvitation.objects.filter(
                                event=event,
                                athlete=athlete,
                                status='pending'
                            ).exists()
                            
                            if not existing:
                                invitation = EventInvitation.objects.create(
                                    event=event,
                                    invitation_type='athlete',
                                    athlete=athlete,
                                    sent_by=user,
                                    message=data.get('message', ''),
                                    expires_at=data.get('expires_at'),
                                    organization_id=org.id
                                )
                                created_invitations.append(invitation)
                                
                                Notification.objects.create(
                                    user=athlete.user,
                                    title=f"Приглашение на мероприятие",
                                    message=f"Вас пригласили на мероприятие '{event.title}' от организации {org.name}.",
                                    notification_type='event_invitation',
                                    related_object_id=invitation.id
                                )
                    
                    # Приглашаем тренеров организации
                    for group in groups:
                        if group.coach:
                            existing = EventInvitation.objects.filter(
                                event=event,
                                coach=group.coach,
                                status='pending'
                            ).exists()
                            
                            if not existing:
                                invitation = EventInvitation.objects.create(
                                    event=event,
                                    invitation_type='coach',
                                    coach=group.coach,
                                    sent_by=user,
                                    message=data.get('message', ''),
                                    expires_at=data.get('expires_at'),
                                    organization_id=org.id
                                )
                                created_invitations.append(invitation)
                                
                                Notification.objects.create(
                                    user=group.coach.user,
                                    title=f"Приглашение на мероприятие",
                                    message=f"Вас пригласили на мероприятие '{event.title}' в качестве тренера от организации {org.name}.",
                                    notification_type='event_invitation',
                                    related_object_id=invitation.id
                                )
                except Organization.DoesNotExist:
                    errors.append(f"Организация с ID {data['organization_id']} не найдена")
            
            # Приглашения для детей родителя
            if hasattr(user, 'parent_profile'):
                children = user.parent_profile.children.all()
                for child_link in children:
                    athlete = child_link.athlete
                    
                    existing = EventInvitation.objects.filter(
                        event=event,
                        athlete=athlete,
                        status='pending'
                    ).exists()
                    
                    if existing:
                        continue
                    
                    invitation = EventInvitation.objects.create(
                        event=event,
                        invitation_type='athlete',
                        athlete=athlete,
                        sent_by=user,
                        message=data.get('message', ''),
                        expires_at=data.get('expires_at')
                    )
                    created_invitations.append(invitation)
                    
                    Notification.objects.create(
                        user=athlete.user,
                        title=f"Приглашение на мероприятие",
                        message=f"Ваш родитель пригласил вас на мероприятие '{event.title}'.",
                        notification_type='event_invitation',
                        related_object_id=invitation.id
                    )
        
        return Response({
            "message": f"Создано приглашений: {len(created_invitations)}",
            "created_count": len(created_invitations),
            "errors": errors if errors else None
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_invitations(request):
    """Получить приглашения пользователя"""
    user = request.user
    
    invitations = EventInvitation.objects.filter(
        Q(athlete__user=user) | Q(coach__user=user),
        status='pending'
    ).select_related('event', 'event__city', 'sent_by', 'athlete', 'athlete__user', 'coach', 'coach__user')
    
    serializer = EventInvitationSerializer(invitations, many=True)
    return Response({"invitations": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_invitation(request, invitation_id):
    """Ответить на приглашение (принять/отклонить)"""
    try:
        invitation = EventInvitation.objects.get(id=invitation_id)
        
        # Проверяем права
        user = request.user
        if invitation.athlete and invitation.athlete.user != user:
            return Response({"error": "Нет доступа"}, status=403)
        if invitation.coach and invitation.coach.user != user:
            return Response({"error": "Нет доступа"}, status=403)
        
        action = request.data.get('action')  # 'accept' или 'decline'
        
        if action == 'accept':
            invitation.status = 'accepted'
            invitation.save()
            
            # Создаём регистрацию
            if invitation.invitation_type == 'athlete' and invitation.athlete:
                EventRegistration.objects.get_or_create(
                    event=invitation.event,
                    registration_type='athlete',
                    athlete=invitation.athlete,
                    defaults={
                        'status': 'registered',
                        'invitation': invitation
                    }
                )
            elif invitation.invitation_type == 'coach' and invitation.coach:
                EventRegistration.objects.get_or_create(
                    event=invitation.event,
                    registration_type='coach',
                    coach=invitation.coach,
                    defaults={
                        'status': 'registered',
                        'invitation': invitation
                    }
                )
            
            return Response({"message": "Приглашение принято"})
        
        elif action == 'decline':
            invitation.status = 'declined'
            invitation.save()
            return Response({"message": "Приглашение отклонено"})
        
        else:
            return Response({"error": "Неверное действие"}, status=400)
    
    except EventInvitation.DoesNotExist:
        return Response({"error": "Приглашение не найдено"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
