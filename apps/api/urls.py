# apps/api/urls.py
"""
Централизованный роутер для всех API endpoints
"""
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Аутентификация
    path('auth/', include('apps.authn.api.urls')),
    
    # Пользователи
    path('users/', include('apps.users.api.urls')),
    
    # Организации
    path('organizations/', include('apps.organizations.api.urls')),
    
    # Спортсмены
    path('athletes/', include('apps.athletes.api.urls')),
    
    # Родители
    path('parents/', include('apps.parents.api.urls')),
    
    # Тренеры
    path('coaches/', include('apps.coaches.api.urls')),
    
    # Посещаемость
    path('attendance/', include('apps.attendance.api.urls')),
    
    # Мероприятия
    path('events/', include('apps.events.api.urls')),
    
    # Городской комитет
    path('city-committee/', include('apps.city_committee.api.urls')),
    
    # География
    path('geography/', include('apps.geography.api.urls')),
    
    # Виды спорта
    path('sports/', include('apps.sports.api.urls')),
    
    # Админ РБ
    path('admin-rb/', include('apps.admin_rb.api.urls')),
    
    # Тренировки и группы
    path('training/', include('apps.training.api.urls')),
    
    # Файлы
    path('files/', include('apps.files.api.urls')),
    
    # Достижения
    path('achievements/', include('apps.achievements.api.urls')),
    
    # Core (константы, согласия, health check)
    path('core/', include('apps.core.api.urls')),
    
    # Аудит
    path('audit/', include('apps.audit.api.urls')),
    
    # Аналитика
    path('analytics/', include('apps.analytics.api.urls')),
    
    # Уведомления
    path('notifications/', include('apps.notifications.api.urls')),
]
