# apps/authn/api/urls.py
from django.urls import path
from django.http import JsonResponse
from .views import LoginView, register, vk_login, telegram_login, vk_oauth_start, vk_oauth_callback

def auth_index(request):
    """Информация об API аутентификации"""
    return JsonResponse({
        'endpoints': {
            'login': '/api/auth/login/',
            'register': '/api/auth/register/',
            'vk': '/api/auth/vk/',
            'telegram': '/api/auth/telegram/',
        },
        'methods': {
            'login': 'POST',
            'register': 'POST',
            'vk': 'POST',
            'telegram': 'POST',
        }
    })

urlpatterns = [
    path('', auth_index, name='auth-index'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('register/', register, name='auth-register'),
    path('vk/', vk_oauth_start, name='vk-oauth-start'),  # Начало OAuth flow
    path('vk/callback/', vk_oauth_callback, name='vk-oauth-callback'),  # Callback от VK
    path('vk/token/', vk_login, name='vk-login'),  # Прямая авторизация по токену (для обратной совместимости)
    path('telegram/', telegram_login, name='telegram-login'),
]