# config/settings/auth.py
from datetime import timedelta
from .base import *

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# OAuth2 (VK)
VK_CLIENT_ID = os.getenv('VK_CLIENT_ID')
VK_CLIENT_SECRET = os.getenv('VK_CLIENT_SECRET')
# Для локальной разработки используем localhost, для production - реальный домен
if DEBUG:
    VK_REDIRECT_URI = os.getenv('VK_REDIRECT_URI', 'http://127.0.0.1:8060/api/auth/vk/callback/')
else:
    VK_REDIRECT_URI = os.getenv('VK_REDIRECT_URI', 'https://sportbash.ru/api/auth/vk/callback/')

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_WEBAPP_DOMAIN = os.getenv('TELEGRAM_WEBAPP_DOMAIN', 'https://sportbash.ru')