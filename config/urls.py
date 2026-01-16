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
]