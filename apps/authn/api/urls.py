# apps/authn/api/urls.py
from django.urls import path
from .views import LoginView, register, vk_login, telegram_login

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('register/', register, name='auth-register'),
    path('vk/', vk_login, name='vk-login'),
    path('telegram/', telegram_login, name='telegram-login'),
]