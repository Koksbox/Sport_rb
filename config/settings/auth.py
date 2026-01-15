import os

# JWT Settings
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_LIFETIME = timedelta(hours=2)
JWT_REFRESH_TOKEN_LIFETIME = timedelta(days=7)

# OAuth Settings
VK_OAUTH_CLIENT_ID = os.getenv('VK_OAUTH_CLIENT_ID', '')
VK_OAUTH_CLIENT_SECRET = os.getenv('VK_OAUTH_CLIENT_SECRET', '')
VK_OAUTH_REDIRECT_URI = os.getenv('VK_OAUTH_REDIRECT_URI', 'http://localhost:8000/auth/vk/callback')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', '')

# Email verification
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# 2FA Settings
TWO_FACTOR_ENABLED = os.getenv('TWO_FACTOR_ENABLED', 'False') == 'True'
TWO_FACTOR_ISSUER_NAME = 'SportBash'
