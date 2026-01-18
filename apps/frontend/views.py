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
    
    # Проверяем, есть ли у пользователя роль
    if not user.roles.exists():
        # Если роли нет, показываем выбор роли
        return render(request, 'frontend/dashboard.html', {
            'user': user,
            'has_role': False,
        })
    
    # Определяем основную роль пользователя
    user_role = user.roles.first().role
    
    # Выбираем шаблон в зависимости от роли
    if user_role == 'athlete':
        return render(request, 'frontend/dashboard_athlete.html', {'user': user})
    elif user_role == 'parent':
        return render(request, 'frontend/dashboard_parent.html', {'user': user})
    elif user_role == 'coach':
        return render(request, 'frontend/dashboard_coach.html', {'user': user})
    elif user_role == 'organization' or user_role == 'director':
        return render(request, 'frontend/dashboard_organization.html', {'user': user})
    else:
        # Для других ролей используем базовый шаблон
        return render(request, 'frontend/dashboard.html', {
            'user': user,
            'has_role': True,
        })

@login_required
def role_selection(request):
    """Страница выбора роли"""
    return render(request, 'frontend/role_selection.html')

def organizations_list(request):
    """Список организаций (публичная страница)"""
    return render(request, 'frontend/organizations/list.html')

@login_required
def organization_create(request):
    """Создание организации (требует авторизации)"""
    return render(request, 'frontend/organizations/create.html')

def events_list(request):
    """Список мероприятий (публичная страница)"""
    return render(request, 'frontend/events/list.html')

def event_detail_page(request, event_id):
    """Детальная страница мероприятия (публичная страница)"""
    context = {'event_id': event_id}
    return render(request, 'frontend/events/detail.html', context)
