# apps/frontend/settings.py
"""
Настройки для Frontend приложения
"""
from django.conf import settings

# Frontend специфичные настройки
FRONTEND_TITLE = 'СпортБаш'
FRONTEND_DESCRIPTION = 'Единая цифровая спортивная экосистема Республики Башкортостан'

# Настройки для статических файлов
STATIC_URL = getattr(settings, 'STATIC_URL', '/static/')
MEDIA_URL = getattr(settings, 'MEDIA_URL', '/media/')

# Настройки для Telegram Mini App
TELEGRAM_BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)

# Настройки для социальных сетей
VK_APP_ID = getattr(settings, 'VK_APP_ID', None)
VK_APP_SECRET = getattr(settings, 'VK_APP_SECRET', None)
