# apps/users/api/profile_views.py
"""
API для просмотра профилей пользователей по ID роли с ограничениями доступа
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import UserRole, CustomUser
from apps.athletes.models import AthleteProfile
from apps.coaches.models import CoachProfile
from apps.achievements.models import Achievement, CoachAchievement

def can_view_profile(viewer, target_role):
    """
    Проверяет, может ли пользователь просматривать профиль роли
    
    Правила:
    - Спортсмены и тренеры могут просматривать только профили спортсменов и тренеров
    - Главный админ может просматривать все профили
    - Сотрудники спорткомитета могут просматривать все профили кроме главного админа
    - Родители, директора организаций, админы не могут просматривать профили (кроме своих)
    - Главный админ может просматривать только свой профиль
    """
    # Пользователь всегда может просматривать свой профиль
    if viewer == target_role.user:
        return True
    
    # Проверяем роль главного админа
    is_main_admin = viewer.roles.filter(role='admin_rb', is_active=True).exists()
    is_committee_staff = viewer.roles.filter(role='committee_staff', is_active=True).exists()
    
    # Главный админ может просматривать только свой профиль
    if target_role.role == 'admin_rb':
        return viewer == target_role.user
    
    # Главный админ и сотрудники спорткомитета могут просматривать профили спортсменов и тренеров
    if is_main_admin or is_committee_staff:
        # Но не могут просматривать профили родителя, директора, админа (кроме своих)
        if target_role.role in ['parent', 'director', 'admin_rb']:
            return False
        # Могут просматривать только спортсменов и тренеров
        if target_role.role in ['athlete', 'coach']:
            return True
        return False
    
    # Обычные пользователи могут просматривать только профили спортсменов и тренеров
    if target_role.role in ['athlete', 'coach']:
        # Проверяем, что просматривающий тоже спортсмен или тренер
        viewer_roles = viewer.roles.filter(role__in=['athlete', 'coach'], is_active=True)
        return viewer_roles.exists()
    
    # Все остальные роли не могут просматриваться
    return False

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_by_role_id(request):
    """Поиск пользователя по ID роли"""
    role_id = request.query_params.get('id', '').strip().upper()
    
    if not role_id or len(role_id) != 8:
        return Response(
            {'error': 'Укажите корректный ID роли (8 символов)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        target_role = UserRole.objects.select_related('user').get(unique_id=role_id, is_active=True)
    except UserRole.DoesNotExist:
        return Response(
            {'error': 'Роль с таким ID не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Проверяем права доступа
    if not can_view_profile(request.user, target_role):
        return Response(
            {'error': 'У вас нет доступа для просмотра этого профиля'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Формируем данные профиля в зависимости от роли
    profile_data = {
        'role_id': target_role.unique_id,
        'role': target_role.role,
        'user_id': target_role.user.id,
        'user_name': target_role.user.get_full_name(),
        'user_email': target_role.user.email if request.user == target_role.user else None,
    }
    
    if target_role.role == 'athlete':
        try:
            athlete_profile = target_role.user.athlete_profile
            profile_data.update({
                'city': athlete_profile.city.name if athlete_profile.city else None,
                'main_sport': athlete_profile.main_sport.name if athlete_profile.main_sport else None,
                'birth_date': athlete_profile.birth_date,
                'photo_url': request.build_absolute_uri(athlete_profile.user.photo.url) if athlete_profile.user.photo else None,
            })
        except AthleteProfile.DoesNotExist:
            pass
    
    elif target_role.role == 'coach':
        try:
            coach_profile = target_role.user.coach_profile
            profile_data.update({
                'city': coach_profile.city.name if coach_profile.city else None,
                'specialization': coach_profile.specialization.name if coach_profile.specialization else None,
                'experience_years': coach_profile.experience_years,
                'photo_url': request.build_absolute_uri(coach_profile.user.photo.url) if coach_profile.user.photo else None,
            })
        except CoachProfile.DoesNotExist:
            pass
    
    return Response(profile_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_profile_by_role_id(request, role_id):
    """Просмотр полного профиля по ID роли"""
    role_id = role_id.upper()
    
    try:
        target_role = UserRole.objects.select_related('user').get(unique_id=role_id, is_active=True)
    except UserRole.DoesNotExist:
        return Response(
            {'error': 'Роль с таким ID не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Проверяем права доступа
    if not can_view_profile(request.user, target_role):
        return Response(
            {'error': 'У вас нет доступа для просмотра этого профиля'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Формируем полные данные профиля
    profile_data = {
        'role_id': target_role.unique_id,
        'role': target_role.role,
        'user_id': target_role.user.id,
        'user_name': target_role.user.get_full_name(),
        'user_email': target_role.user.email if request.user == target_role.user else None,
        'user_phone': target_role.user.phone if request.user == target_role.user else None,
    }
    
    if target_role.role == 'athlete':
        try:
            athlete_profile = target_role.user.athlete_profile
            achievements = Achievement.objects.filter(athlete=athlete_profile).order_by('-date')[:10]
            
            profile_data.update({
                'city': athlete_profile.city.name if athlete_profile.city else None,
                'main_sport': athlete_profile.main_sport.name if athlete_profile.main_sport else None,
                'birth_date': athlete_profile.birth_date,
                'photo_url': request.build_absolute_uri(athlete_profile.user.photo.url) if athlete_profile.user.photo else None,
                'achievements': [
                    {
                        'id': a.id,
                        'title': a.title,
                        'achievement_type': a.achievement_type,
                        'date': a.date,
                        'photo_url': request.build_absolute_uri(a.photo.url) if a.photo else None,
                        'description': a.description,
                    }
                    for a in achievements
                ],
            })
        except AthleteProfile.DoesNotExist:
            pass
    
    elif target_role.role == 'coach':
        try:
            coach_profile = target_role.user.coach_profile
            achievements = CoachAchievement.objects.filter(coach=coach_profile).order_by('-date')[:10]
            
            profile_data.update({
                'city': coach_profile.city.name if coach_profile.city else None,
                'specialization': coach_profile.specialization.name if coach_profile.specialization else None,
                'experience_years': coach_profile.experience_years,
                'education': coach_profile.education if request.user == target_role.user else None,
                'photo_url': request.build_absolute_uri(coach_profile.user.photo.url) if coach_profile.user.photo else None,
                'achievements': [
                    {
                        'id': a.id,
                        'title': a.title,
                        'achievement_type': a.achievement_type,
                        'date': a.date,
                        'photo_url': request.build_absolute_uri(a.photo.url) if a.photo else None,
                        'description': a.description,
                        'issued_by': a.issued_by,
                    }
                    for a in achievements
                ],
            })
        except CoachProfile.DoesNotExist:
            pass
    
    return Response(profile_data)
