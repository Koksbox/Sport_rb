# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Регистрация и вход, выбор роли
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authn.api.urls')),
    path('api/users/', include('apps.users.api.urls')),
    # Создание организации, модератор
    path('api/organizations/', include('apps.organizations.api.urls')),
    path('api/athletes/', include('apps.athletes.api.urls')),
    # Родитель
    path('api/parents/', include('apps.parents.api.urls')),
    # Тренер
    path('api/coaches/', include('apps.coaches.api.urls')),
    # Клуб
    path('api/attendance/', include('apps.attendance.api.urls')),
    # Мероприятия
    path('api/events/', include('apps.events.api.urls')),
    # Госскомитет
    path('api/city-committee/', include('apps.city_committee.api.urls')),
    # География
    path('api/geography/', include('apps.geography.api.urls')),
    # Спорт категории и список
    path('api/sports/', include('apps.sports.api.urls')),
    # Админ РБ
    path('api/admin-rb/', include('apps.admin_rb.api.urls')),
    # Группы
    path('api/training/', include('apps.training.api.urls')),
    # Файлы
    path('api/files/', include('apps.files.api.urls')),
    # Достижения
    path('api/achievements/', include('apps.achievements.api.urls')),
    # Core
    path('api/core/', include('apps.core.api.urls')),
    # Логи
    path('api/audit/', include('apps.audit.api.urls')),
    # Статистика
    path('api/analytics/', include('apps.analytics.api.urls')),
    # Уведомления
    path('api/notifications/', include('apps.notifications.api.urls')),
]