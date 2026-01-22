# apps/coaches/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    TrainingGroupSerializer, ClubSearchSerializer, ClubRequestSerializer, CoachProfileSerializer,
    FreeOrganizationSerializer, FreeCoachSerializer, CoachInvitationSerializer, CoachInvitationCreateSerializer,
    ClubRequestDetailSerializer
)
from apps.training.models import Enrollment
from apps.notifications.models import Notification
from apps.coaches.models import ClubRequest, CoachInvitation
from apps.organizations.models import Organization
from apps.organizations.staff.coach_membership import CoachMembership
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coach_organizations(request):
    """Получить список организаций, в которых работает тренер"""
    try:
        coach = request.user.coach_profile
        memberships = coach.coach_memberships.filter(status='active').select_related('organization', 'organization__city')
        
        organizations = []
        for membership in memberships:
            org = membership.organization
            organizations.append({
                'id': org.id,
                'name': org.name,
                'city_name': org.city.name if org.city else None,
                'org_type': org.org_type,
                'address': org.address,
            })
        
        return Response({'organizations': organizations})
    except Exception as e:
        return Response({"error": "Профиль тренера не найден", "detail": str(e)}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_groups(request, org_id):
    """Получить группы организации, в которых работает тренер"""
    try:
        from apps.organizations.models import Organization
        from apps.organizations.staff.coach_membership import CoachMembership
        
        organization = Organization.objects.get(id=org_id)
        coach = request.user.coach_profile
        
        # Проверка доступа
        membership = CoachMembership.objects.filter(
            coach=coach, organization=organization, status='active'
        ).first()
        
        if not membership:
            return Response({"error": "Нет доступа к этой организации"}, status=403)
        
        groups = membership.groups.all().select_related('sport', 'age_level', 'organization')
        serializer = TrainingGroupSerializer(groups, many=True, context={'request': request})
        return Response(serializer.data)
    except Organization.DoesNotExist:
        return Response({"error": "Организация не найдена"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def get_coach_profile(request):
    """Получить или обновить профиль тренера"""
    try:
        profile = request.user.coach_profile
        user = request.user
        
        if request.method == 'GET':
            # Возвращаем данные пользователя и профиля
            from apps.users.api.serializers import UserBasicSerializer
            from .serializers import CoachProfileSerializer
            user_serializer = UserBasicSerializer(user, context={'request': request})
            profile_serializer = CoachProfileSerializer(profile, context={'request': request})
            
            data = user_serializer.data
            profile_data = profile_serializer.data
            # Добавляем city_id и specialization_id для удобства
            profile_data['city_id'] = profile.city.id if profile.city else None
            profile_data['specialization_id'] = profile.specialization.id if profile.specialization else None
            data.update(profile_data)
            return Response(data)
        
        elif request.method == 'PATCH':
            # Обновляем данные пользователя
            from apps.users.api.serializers import UserBasicSerializer
            from .serializers import CoachProfileSerializer
            user_data = {}
            profile_data = {}
            
            # Общие данные пользователя (ФИО, фото, дата рождения, пол, город) 
            # редактируются отдельно через /api/users/basic-data/
            # Здесь обрабатываем только специфичные для тренера поля
            
            # Остальные данные идут в профиль
            profile_fields = ['phone', 'telegram', 'experience_years', 'education']
            for field in profile_fields:
                if field in request.data:
                    profile_data[field] = request.data[field]
            
            # Обрабатываем city_id отдельно (для профиля тренера)
            if 'city_id' in request.data:
                profile_data['city_id'] = request.data['city_id']
            
            # Обрабатываем specialization отдельно
            if 'specialization' in request.data:
                profile_data['specialization_id'] = request.data['specialization']
            elif 'specialization_id' in request.data:
                profile_data['specialization_id'] = request.data['specialization_id']
            
            # Обновляем пользователя
            if user_data:
                user_serializer = UserBasicSerializer(user, data=user_data, partial=True, context={'request': request})
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    return Response(user_serializer.errors, status=400)
            
            # Обновляем профиль
            if profile_data:
                profile_serializer = CoachProfileSerializer(profile, data=profile_data, partial=True, context={'request': request})
                if profile_serializer.is_valid():
                    profile_serializer.save()
                else:
                    return Response(profile_serializer.errors, status=400)
            
            # Возвращаем обновленные данные
            user_serializer = UserBasicSerializer(user, context={'request': request})
            profile_serializer = CoachProfileSerializer(profile, context={'request': request})
            data = user_serializer.data
            profile_data = profile_serializer.data
            # Добавляем city_id и specialization_id для удобства
            profile_data['city_id'] = profile.city.id if profile.city else None
            profile_data['specialization_id'] = profile.specialization.id if profile.specialization else None
            data.update(profile_data)
            return Response(data)
            
    except Exception as e:
        return Response({"error": "Профиль тренера не найден", "detail": str(e)}, status=404)


# ========== НОВЫЕ ФУНКЦИИ ДЛЯ СИСТЕМЫ ЗАЯВОК И ПРИГЛАШЕНИЙ ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_free_organizations(request):
    """Получить список свободных организаций, куда тренер может подать заявку"""
    try:
        coach = request.user.coach_profile
        
        # Получаем организации, где тренер уже работает
        active_orgs = CoachMembership.objects.filter(
            coach=coach, status='active'
        ).values_list('organization_id', flat=True)
        
        # Получаем организации, куда уже подана заявка
        pending_orgs = ClubRequest.objects.filter(
            coach=coach, status__in=['pending', 'approved']
        ).values_list('organization_id', flat=True)
        
        # Исключаем эти организации
        excluded_orgs = set(list(active_orgs) + list(pending_orgs))
        
        # Получаем только одобренные организации
        queryset = Organization.objects.filter(
            status='approved'
        ).exclude(id__in=excluded_orgs)
        
        # Фильтры
        city_id = request.query_params.get('city_id')
        sport_id = request.query_params.get('sport_id')
        
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if sport_id:
            queryset = queryset.filter(sport_directions__sport_id=sport_id).distinct()
        
        serializer = FreeOrganizationSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coach_requests_for_director(request):
    """Получить список заявок от тренеров для директора"""
    try:
        if not hasattr(request.user, 'director_role'):
            return Response({"error": "Только директор может просматривать заявки"}, status=403)
        
        director = request.user.director_role
        organization = director.organization
        
        requests = ClubRequest.objects.filter(
            organization=organization,
            status='pending'
        ).select_related('coach', 'coach__user', 'specialization', 'organization')
        
        serializer = ClubRequestDetailSerializer(requests, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_coach_request_by_director(request, request_id):
    """Директор одобряет заявку тренера"""
    try:
        if not hasattr(request.user, 'director_role'):
            return Response({"error": "Только директор может одобрять заявки"}, status=403)
        
        director = request.user.director_role
        organization = director.organization
        
        club_request = ClubRequest.objects.get(
            id=request_id,
            organization=organization,
            status='pending'
        )
        
        club_request.status = 'approved'
        club_request.save()
        
        coach = club_request.coach
        
        # Создаем членство
        from apps.users.models import UserRole
        UserRole.objects.get_or_create(user=coach.user, role='coach')
        
        membership, _ = CoachMembership.objects.get_or_create(
            coach=coach,
            organization=organization,
            defaults={'status': 'active'}
        )
        
        # Уведомление тренеру
        Notification.objects.create(
            recipient=coach.user,
            notification_type='coach_request_approved',
            title='Ваша заявка одобрена',
            body=f'Директор организации "{organization.name}" одобрил вашу заявку на работу.'
        )
        
        return Response({"message": "Заявка одобрена"})
    except ClubRequest.DoesNotExist:
        return Response({"error": "Заявка не найдена"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_coach_request_by_director(request, request_id):
    """Директор отклоняет заявку тренера"""
    try:
        if not hasattr(request.user, 'director_role'):
            return Response({"error": "Только директор может отклонять заявки"}, status=403)
        
        director = request.user.director_role
        organization = director.organization
        
        club_request = ClubRequest.objects.get(
            id=request_id,
            organization=organization,
            status='pending'
        )
        
        rejected_reason = request.data.get('rejected_reason', '')
        club_request.status = 'rejected'
        club_request.rejected_reason = rejected_reason
        club_request.save()
        
        # Уведомление тренеру
        Notification.objects.create(
            recipient=club_request.coach.user,
            notification_type='coach_request_rejected',
            title='Ваша заявка отклонена',
            body=f'Директор организации "{organization.name}" отклонил вашу заявку на работу.'
        )
        
        return Response({"message": "Заявка отклонена"})
    except ClubRequest.DoesNotExist:
        return Response({"error": "Заявка не найдена"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_free_coaches_for_director(request):
    """Получить список свободных тренеров для директора"""
    try:
        if not hasattr(request.user, 'director_role'):
            return Response({"error": "Только директор может просматривать тренеров"}, status=403)
        
        director = request.user.director_role
        organization = director.organization
        
        # Получаем тренеров, которые уже работают в организации
        active_coaches = CoachMembership.objects.filter(
            organization=organization, status='active'
        ).values_list('coach_id', flat=True)
        
        # Получаем тренеров, которым уже отправлено приглашение
        invited_coaches = CoachInvitation.objects.filter(
            organization=organization, status='pending'
        ).values_list('coach_id', flat=True)
        
        # Исключаем этих тренеров
        excluded_coaches = set(list(active_coaches) + list(invited_coaches))
        
        from apps.coaches.models import CoachProfile
        queryset = CoachProfile.objects.exclude(id__in=excluded_coaches)
        
        # Фильтры
        city_id = request.query_params.get('city_id')
        sport_id = request.query_params.get('sport_id')
        
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if sport_id:
            queryset = queryset.filter(specialization_id=sport_id)
        
        serializer = FreeCoachSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_coach_invitation(request):
    """Директор отправляет приглашение тренеру"""
    serializer = CoachInvitationCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        invitation = serializer.save()
        
        # Уведомление тренеру
        Notification.objects.create(
            recipient=invitation.coach.user,
            notification_type='coach_invitation',
            title='Приглашение на работу',
            body=f'Организация "{invitation.organization.name}" приглашает вас на работу.'
        )
        
        response_serializer = CoachInvitationSerializer(invitation)
        return Response(response_serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coach_invitations(request):
    """Получить список приглашений для тренера"""
    try:
        coach = request.user.coach_profile
        invitations = CoachInvitation.objects.filter(
            coach=coach,
            status='pending'
        ).select_related('organization', 'organization__city', 'specialization')
        
        serializer = CoachInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_coach_invitation(request, invitation_id):
    """Тренер принимает приглашение"""
    try:
        coach = request.user.coach_profile
        invitation = CoachInvitation.objects.get(
            id=invitation_id,
            coach=coach,
            status='pending'
        )
        
        invitation.status = 'accepted'
        invitation.responded_at = timezone.now()
        invitation.save()
        
        # Создаем членство
        from apps.users.models import UserRole
        UserRole.objects.get_or_create(user=coach.user, role='coach')
        
        membership, _ = CoachMembership.objects.get_or_create(
            coach=coach,
            organization=invitation.organization,
            defaults={'status': 'active'}
        )
        
        # Уведомление директору
        director = invitation.organization.director.user
        Notification.objects.create(
            recipient=director,
            notification_type='coach_invitation_accepted',
            title='Тренер принял приглашение',
            body=f'Тренер {coach.user.get_full_name()} принял ваше приглашение на работу.'
        )
        
        return Response({"message": "Приглашение принято"})
    except CoachInvitation.DoesNotExist:
        return Response({"error": "Приглашение не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_coach_invitation(request, invitation_id):
    """Тренер отклоняет приглашение"""
    try:
        coach = request.user.coach_profile
        invitation = CoachInvitation.objects.get(
            id=invitation_id,
            coach=coach,
            status='pending'
        )
        
        invitation.status = 'rejected'
        invitation.responded_at = timezone.now()
        invitation.save()
        
        # Уведомление директору
        director = invitation.organization.director.user
        Notification.objects.create(
            recipient=director,
            notification_type='coach_invitation_rejected',
            title='Тренер отклонил приглашение',
            body=f'Тренер {coach.user.get_full_name()} отклонил ваше приглашение на работу.'
        )
        
        return Response({"message": "Приглашение отклонено"})
    except CoachInvitation.DoesNotExist:
        return Response({"error": "Приглашение не найдено"}, status=404)
    except Exception as e:
        return Response({"error": "Ошибка", "detail": str(e)}, status=500)