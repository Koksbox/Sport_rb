DEBUG = True

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

CORS_ALLOW_ALL_ORIGINS = True

# Для разработки - упрощённые настройки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Отключаем некоторые проверки безопасности для разработки
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
