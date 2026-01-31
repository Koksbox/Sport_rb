# apps/frontend/views_auth.py
"""
Views для аутентификации через сессии Django (для совместимости с login_required)
"""
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from apps.users.models import UserRole

@require_http_methods(["GET", "POST"])
def django_login(request):
    """
    Вход через сессии Django (для совместимости с @login_required)
    Редиректит на страницу входа фронтенда, если GET запрос
    """
    if request.user.is_authenticated:
        next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        return redirect(next_url)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            # Аутентификация через email (USERNAME_FIELD = 'email')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Если пользователь - суперпользователь, создаём роль admin_rb, если её нет
                if user.is_superuser:
                    admin_role, created = UserRole.objects.get_or_create(
                        user=user,
                        role='admin_rb',
                        defaults={'is_active': True}
                    )
                    # Устанавливаем admin_rb как активную роль
                    request.session['active_role'] = 'admin_rb'
                elif user.roles.exists():
                    # Для обычных пользователей устанавливаем первую доступную роль
                    first_role = user.roles.filter(is_active=True).first()
                    if first_role:
                        request.session['active_role'] = first_role.role
                
                next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный email или пароль.')
        else:
            messages.error(request, 'Заполните все поля.')
    
    # Редирект на страницу входа фронтенда
    next_param = request.GET.get('next', '')
    redirect_url = '/login/'
    if next_param:
        redirect_url += f'?next={next_param}'
    return redirect(redirect_url)
