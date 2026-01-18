# apps/api/settings.py
"""
Настройки для API приложения
"""
from django.conf import settings

# API специфичные настройки
API_VERSION = 'v1'
API_TITLE = 'СпортБаш API'
API_DESCRIPTION = 'API для единой цифровой спортивной экосистемы Республики Башкортостан'

# CORS настройки для API
CORS_ALLOWED_ORIGINS = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
CORS_ALLOW_CREDENTIALS = True

# Настройки для DRF
REST_FRAMEWORK_SETTINGS = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
