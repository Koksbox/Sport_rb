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
    """Личный кабинет с разными интерфейсами для разных ролей"""
    user = request.user
    
    # Получаем активную роль из сессии или первую доступную
    active_role = request.session.get('active_role')
    if not active_role and user.roles.exists():
        active_role = user.roles.first().role
        request.session['active_role'] = active_role
    
    # Если роли нет, показываем выбор роли
    if not user.roles.exists():
        return render(request, 'frontend/dashboard.html', {
            'user': user,
            'has_role': False,
            'all_roles': [],
        })
    
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

def event_detail_page(request, event_id):
    """Детальная страница мероприятия (публичная страница)"""
    context = {'event_id': event_id}
    return render(request, 'frontend/events/detail.html', context)

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

def logout_view(request):
    """Выход из аккаунта"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('frontend-index')

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