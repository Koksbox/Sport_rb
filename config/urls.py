# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Импортируем админки для регистрации моделей
import apps.core.admin  # Кастомизация админ-сайта
import apps.users.admin
import apps.geography.admin
import apps.sports.admin
import apps.organizations.admin
import apps.athletes.admin
import apps.coaches.admin
import apps.parents.admin
import apps.events.admin
import apps.training.admin
import apps.attendance.admin
import apps.achievements.admin
import apps.files.admin
import apps.notifications.admin
import apps.city_committee.admin
import apps.admin_rb.admin
import apps.audit.admin
import apps.authn.admin

urlpatterns = [
    # Админ панель Django
    path('admin/', admin.site.urls),
    
    # API - все endpoints под /api/
    path('api/', include('apps.api.urls')),
    
    # Frontend - все остальные пути
    path('', include('apps.frontend.urls')),
]

# Раздача статических и медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)