# apps/frontend/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings

def get_api_url(path):
    """Получить полный URL для API запроса"""
    return f"/api{path}"

def index(request):
    """Главная страница"""
    return render(request, 'frontend/index.html')

def login_page(request):
    """Страница входа"""
    return render(request, 'frontend/auth/login.html')

def register_page(request):
    """Страница регистрации"""
    return render(request, 'frontend/auth/register.html')

@login_required
def dashboard(request):
    """Личный кабинет с переключением ролей"""
    from apps.users.models import UserRole
    
    user = request.user
    
    # Если пользователь - суперпользователь, создаём роль admin_rb, если её нет
    if user.is_superuser:
        admin_role, created = UserRole.objects.get_or_create(
            user=user,
            role='admin_rb',
            defaults={'is_active': True}
        )
        # Устанавливаем admin_rb как активную роль
        request.session['active_role'] = 'admin_rb'
        active_role = 'admin_rb'
    else:
        # Получаем активную роль из сессии или первую доступную
        active_role = request.session.get('active_role')
        if not active_role and user.roles.exists():
            active_role = user.roles.filter(is_active=True).first()
            if active_role:
                active_role = active_role.role
                request.session['active_role'] = active_role
    
    # Если роли нет (для обычных пользователей), показываем выбор роли
    if not user.is_superuser and not user.roles.exists():
        return redirect('frontend-new-role-selection')
    
    # Получаем все роли пользователя
    all_roles = list(user.roles.values_list('role', flat=True))
    
    # Выбираем шаблон в зависимости от активной роли
    if active_role == 'athlete':
        return render(request, 'frontend/dashboard_athlete.html', {
            'user': user,
            'active_role': active_role,
            'all_roles': all_roles,
        })
    elif active_role == 'parent':
        return render(request, 'frontend/dashboard_parent.html', {
            'user': user,
            'active_role': active_role,
            'all_roles': all_roles,
        })
    elif active_role == 'coach':
        return render(request, 'frontend/dashboard_coach.html', {
            'user': user,
            'active_role': active_role,
            'all_roles': all_roles,
        })
    elif active_role == 'organization' or active_role == 'director':
        return render(request, 'frontend/dashboard_organization.html', {
            'user': user,
            'active_role': active_role,
            'all_roles': all_roles,
        })
    elif active_role == 'admin_rb':
        return render(request, 'frontend/dashboard_admin.html', {
            'user': user,
            'active_role': active_role,
            'all_roles': all_roles,
        })
    elif active_role == 'committee_staff':
        return render(request, 'frontend/dashboard_committee.html', {
            'user': user,
            'active_role': active_role,
            'all_roles': all_roles,
        })
    else:
        # Для других ролей используем базовый шаблон
        return render(request, 'frontend/dashboard.html', {
            'user': user,
            'has_role': True,
            'active_role': active_role,
            'all_roles': all_roles,
        })

@login_required
def role_selection(request):
    """Страница выбора роли"""
    return render(request, 'frontend/role_selection.html')

@login_required
def role_setup_athlete(request):
    """Страница заполнения данных для роли спортсмена"""
    # Проверяем, нет ли уже этой роли
    if request.user.roles.filter(role='athlete').exists():
        return redirect('frontend-dashboard')
    return render(request, 'frontend/role_setup_athlete.html', {
        'user': request.user,
    })

@login_required
def role_setup_coach(request):
    """Страница заполнения данных для роли тренера"""
    # Проверяем, нет ли уже этой роли
    if request.user.roles.filter(role='coach').exists():
        return redirect('frontend-dashboard')
    return render(request, 'frontend/role_setup_coach.html', {
        'user': request.user,
    })

def organizations_list(request):
    """Список организаций (публичная страница)"""
    from django.conf import settings
    return render(request, 'frontend/organizations/list.html', {
        'YANDEX_MAPS_API_KEY': getattr(settings, 'YANDEX_MAPS_API_KEY', ''),
    })

def organization_detail(request, org_id):
    """Детальная страница организации (публичная страница)"""
    from django.conf import settings
    return render(request, 'frontend/organizations/detail.html', {
        'org_id': org_id,
        'YANDEX_MAPS_API_KEY': getattr(settings, 'YANDEX_MAPS_API_KEY', ''),
    })

@login_required
def organization_create(request):
    """Создание организации (требует авторизации)"""
    from django.conf import settings
    return render(request, 'frontend/organizations/create.html', {
        'YANDEX_MAPS_API_KEY': getattr(settings, 'YANDEX_MAPS_API_KEY', ''),
    })

def events_list(request):
    """Список мероприятий (публичная страница)"""
    return render(request, 'frontend/events/list.html')

@login_required
def my_events_page(request):
    """Страница "Мои мероприятия" - зарегистрированные мероприятия пользователя"""
    return render(request, 'frontend/events/my_events.html')

@login_required
def event_invitations_page(request):
    """Страница приглашений на мероприятия"""
    return render(request, 'frontend/events/invitations.html')

def event_detail_page(request, event_id):
    """Детальная страница мероприятия (публичная страница)"""
    context = {'event_id': event_id}
    return render(request, 'frontend/events/detail.html', context)

@login_required
def event_registered_page(request, event_id):
    """Страница для зарегистрированных участников мероприятия"""
    # Проверяем, что пользователь зарегистрирован
    return render(request, 'frontend/events/registered.html', {
        'event_id': event_id,
        'user': request.user,
    })

@login_required
def athlete_profile_edit(request):
    """Страница редактирования профиля спортсмена"""
    if not hasattr(request.user, 'athlete_profile'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/athletes/profile_edit.html')

@login_required
def coach_profile_edit(request):
    """Страница редактирования профиля тренера"""
    if not hasattr(request.user, 'coach_profile'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/coaches/profile_edit.html')

@login_required
def coach_find_organization(request):
    """Страница поиска организаций для подачи заявки"""
    if not hasattr(request.user, 'coach_profile'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/coaches/find_organization.html')

@login_required
def coach_organization_groups(request, org_id):
    """Страница управления группами в организации"""
    if not hasattr(request.user, 'coach_profile'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/coaches/organization_groups.html', {'org_id': org_id})

@login_required
def coach_groups_list(request):
    """Список всех групп тренера"""
    if not hasattr(request.user, 'coach_profile'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/coaches/groups_list.html')

@login_required
def coach_group_detail(request, group_id):
    """Детальная страница группы с управлением посещаемостью"""
    if not hasattr(request.user, 'coach_profile'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/coaches/group_detail.html', {'group_id': group_id})

@login_required
def my_organizations(request):
    """Страница "Мои организации" для директора"""
    return render(request, 'frontend/organizations/my.html')

@login_required
def new_role_selection(request):
    """Страница выбора новой роли (для мультиаккаунта)"""
    return render(request, 'frontend/role_selection_new.html')


@login_required
def director_coach_requests(request):
    """Страница заявок от тренеров для директора"""
    if not hasattr(request.user, 'director_role'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/director/coach_requests.html')

@login_required
def director_free_coaches(request):
    """Страница свободных тренеров для директора"""
    if not hasattr(request.user, 'director_role'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/director/free_coaches.html')

@login_required
def coach_invitations(request):
    """Страница приглашений для тренера"""
    if not hasattr(request.user, 'coach_profile'):
        return redirect('frontend-dashboard')
    return render(request, 'frontend/coaches/invitations.html')

@login_required
def user_basic_data_edit(request):
    """Страница редактирования общих данных пользователя"""
    return render(request, 'frontend/users/basic_data_edit.html')

@login_required
def profile_complete(request):
    """Страница заполнения недостающих данных после входа через соцсети (для ФЗ-152)"""
    user = request.user
    # Проверяем, нужна ли эта страница
    needs_completion = not user.phone or not user.city
    if not needs_completion:
        # Если все данные заполнены, редиректим в личный кабинет
        return redirect('frontend-dashboard')
    
    return render(request, 'frontend/users/profile_complete.html', {
        'user': user,
        'missing_phone': not user.phone,
        'missing_city': not user.city,
    })

def logout_view(request):
    """Выход из аккаунта"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('frontend-index')

@login_required
def profile_search(request):
    """Страница поиска профилей по ID роли"""
    return render(request, 'frontend/profiles/search.html')

@login_required
def profile_view(request, role_id):
    """Страница просмотра профиля по ID роли"""
    return render(request, 'frontend/profiles/view.html', {'role_id': role_id})

@login_required
def parent_profile_edit(request):
    """Редактирование профиля родителя"""
    return render(request, 'frontend/parents/profile_edit.html', {
        'user': request.user,
    })

@login_required
def parent_children_list(request):
    """Список детей родителя"""
    return render(request, 'frontend/parents/children_list.html', {
        'user': request.user,
    })

@login_required
def parent_child_detail(request, child_id):
    """Детальный профиль ребёнка"""
    return render(request, 'frontend/parents/child_detail.html', {
        'user': request.user,
        'child_id': child_id,
    })

@login_required
def parent_requests(request):
    """Заявки на связь родитель-ребёнок"""
    return render(request, 'frontend/parents/requests.html', {
        'user': request.user,
    })

@login_required
def admin_dashboard(request):
    """Кабинет главного администратора"""
    # Проверяем права администратора
    if not (request.user.roles.filter(role='admin_rb').exists() or request.user.is_superuser):
        return redirect('frontend-dashboard')
    
    return render(request, 'frontend/dashboard_admin.html', {
        'user': request.user,
    })

@login_required
def committee_register(request):
    """Страница регистрации сотрудника спорткомитета"""
    return render(request, 'frontend/committee/register.html', {
        'user': request.user,
    })

def news_list(request):
    """Страница новостей (публичная)"""
    return render(request, 'frontend/news/list.html')

@login_required
def notifications_list(request):
    """Страница уведомлений пользователя"""
    return render(request, 'frontend/notifications/list.html', {
        'user': request.user,
    })

def about_page(request):
    """Страница "О проекте" (публичная)"""
    return render(request, 'frontend/info/about.html')

def help_page(request):
    """Страница "Помощь" (публичная)"""
    return render(request, 'frontend/info/help.html')

def privacy_policy_page(request):
    """Страница "Политика конфиденциальности" (публичная)"""
    return render(request, 'frontend/info/privacy.html')

def contact_page(request):
    """Страница обратной связи (публичная)"""
    return render(request, 'frontend/info/contact.html')

def offline_page(request):
    """Страница для офлайн режима"""
    return render(request, 'frontend/offline.html')
