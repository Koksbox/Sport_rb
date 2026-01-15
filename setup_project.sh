#!/bin/bash

echo "=== Создание структуры проекта SportBash ==="

# Установка зависимостей
echo "1. Установка зависимостей..."
pip install -r requirements.txt

# Создание базовой структуры
echo "2. Создание структуры проекта..."
mkdir -p config/settings
mkdir -p apps

# Создание приложений
echo "3. Создание приложений Django..."
cd apps

django-admin startapp core
django-admin startapp users
django-admin startapp authn
django-admin startapp geography
django-admin startapp organizations
django-admin startapp sports
django-admin startapp athletes
django-admin startapp parents
django-admin startapp coaches
django-admin startapp training
django-admin startapp attendance
django-admin startapp events
django-admin startapp achievements
django-admin startapp city_committee
django-admin startapp analytics
django-admin startapp notifications
django-admin startapp files
django-admin startapp audit
django-admin startapp admin_rb

cd ..

echo "4. Создание структуры папок внутри приложений..."

# Создаем структуру для каждого приложения
create_app_structure() {
    local app_name=$1
    local app_path="apps/$app_name"

    mkdir -p "$app_path/models"
    mkdir -p "$app_path/migrations"
    mkdir -p "$app_path/services"
    mkdir -p "$app_path/selectors"
    mkdir -p "$app_path/api"
    mkdir -p "$app_path/api/serializers"
    mkdir -p "$app_path/api/views"
    mkdir -p "$app_path/api/urls"
    mkdir -p "$app_path/tests"
    mkdir -p "$app_path/templates/$app_name"

    # Для specific папок
    case $app_name in
        core)
            mkdir -p "$app_path/permissions"
            mkdir -p "$app_path/constants"
            mkdir -p "$app_path/utils"
            mkdir -p "$app_path/middleware"
            ;;
        users)
            mkdir -p "$app_path/permissions"
            ;;
        parents)
            mkdir -p "$app_path/permissions"
            ;;
        coaches)
            mkdir -p "$app_path/history"
            ;;
        city_committee)
            mkdir -p "$app_path/analytics"
            mkdir -p "$app_path/gis"
            ;;
        analytics)
            mkdir -p "$app_path/aggregations"
            mkdir -p "$app_path/exports"
            mkdir -p "$app_path/dashboards"
            ;;
        notifications)
            mkdir -p "$app_path/channels"
            ;;
        files)
            mkdir -p "$app_path/storage"
            ;;
    esac

    # Создаем __init__.py файлы
    touch "$app_path/models/__init__.py"
    touch "$app_path/services/__init__.py"
    touch "$app_path/api/__init__.py"
    touch "$app_path/api/serializers/__init__.py"
    touch "$app_path/api/views/__init__.py"
    touch "$app_path/api/urls/__init__.py"
    touch "$app_path/tests/__init__.py"
}

# Создаем структуру для каждого приложения
for app in core users authn geography organizations sports athletes parents coaches training attendance events achievements city_committee analytics notifications files audit admin_rb; do
    create_app_structure $app
done

# Создаем конфигурационные файлы
echo "5. Создание конфигурационных файлов..."

# config/settings файлы
cat > config/settings/__init__.py << 'EOF'
from .base import *
from .auth import *
from .security import *
from .logging import *
from .integrations import *

try:
    from .local import *
except ImportError:
    pass
EOF

cat > config/settings/base.py << 'EOF'
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-in-production')

DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'corsheaders',
    'phonenumber_field',
    'storages',
    'django_extensions',

    # Local apps
    'apps.core',
    'apps.users',
    'apps.authn',
    'apps.geography',
    'apps.organizations',
    'apps.sports',
    'apps.athletes',
    'apps.parents',
    'apps.coaches',
    'apps.training',
    'apps.attendance',
    'apps.events',
    'apps.achievements',
    'apps.city_committee',
    'apps.analytics',
    'apps.notifications',
    'apps.files',
    'apps.audit',
    'apps.admin_rb',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middleware
    'apps.core.middleware.audit.AuditMiddleware',
    'apps.core.middleware.consent.ConsentMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'sportbash'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

# Phone number
PHONENUMBER_DEFAULT_REGION = 'RU'
PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'
EOF

cat > config/settings/auth.py << 'EOF'
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
EOF

cat > config/settings/security.py << 'EOF'
import os
from cryptography.fernet import Fernet

# Encryption for sensitive data (AES-256)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Генерируем ключ при первом запуске (в продакшене должен быть в env)
    ENCRYPTION_KEY = Fernet.generate_key().decode()

# Data retention policies (in days)
DATA_RETENTION_DAYS = {
    'audit_logs': 365 * 5,  # 5 лет
    'user_inactivity': 365 * 3,  # 3 года неактивности
    'backup_retention': 30,  # 30 дней бэкапов
}

# Password policy
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SYMBOLS = True

# Session security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 1209600  # 2 недели
SESSION_SAVE_EVERY_REQUEST = True

# GDPR/152-ФЗ compliance
CONSENT_REQUIRED_FIELDS = [
    'personal_data',
    'medical_data',
    'marketing_emails',
    'third_party_sharing',
]

CONSENT_RETENTION_PERIOD = 365 * 5  # 5 лет
EOF

cat > config/settings/logging.py << 'EOF'
import os

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'audit': {
            'format': '{asctime} | {user} | {ip} | {action} | {resource} | {status}',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'audit.log'),
            'formatter': 'audit',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'security.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
EOF

cat > config/settings/integrations.py << 'EOF'
import os

# MinIO/S3 Storage
USE_S3 = os.getenv('USE_S3', 'False') == 'True'

if USE_S3:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'ru-1')
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_LOCATION = 'media'
    AWS_DEFAULT_ACL = 'private'
    AWS_QUERYSTRING_AUTH = True

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'

# VK API
VK_API_VERSION = '5.199'
VK_API_BASE_URL = 'https://api.vk.com/method'

# Telegram
TELEGRAM_API_BASE_URL = 'https://api.telegram.org'
TELEGRAM_WEBAPP_URL = os.getenv('TELEGRAM_WEBAPP_URL', 'https://t.me/your_bot/app')

# SMS Gateway
SMS_GATEWAY_API_KEY = os.getenv('SMS_GATEWAY_API_KEY')
SMS_GATEWAY_SENDER = 'SportBash'
SMS_GATEWAY_URL = os.getenv('SMS_GATEWAY_URL')

# GIS Integration
GIS_API_KEY = os.getenv('GIS_API_KEY')
GIS_BASE_URL = 'https://geocode-maps.yandex.ru'
EOF

cat > config/settings/dev.py << 'EOF'
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
EOF

cat > config/settings/prod.py << 'EOF'
DEBUG = False

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Database
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'HOST': os.getenv('DB_HOST'),
    'PORT': os.getenv('DB_PORT'),
    'CONN_MAX_AGE': 600,
}

# Logging
LOGGING['handlers']['file']['level'] = 'ERROR'
LOGGING['loggers']['django']['handlers'] = ['file']

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
EOF

echo "6. Создание основных конфигурационных файлов..."

# config/urls.py
cat > config/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/', include('apps.authn.api.urls')),
        path('users/', include('apps.users.api.urls')),
        path('organizations/', include('apps.organizations.api.urls')),
        path('athletes/', include('apps.athletes.api.urls')),
        path('coaches/', include('apps.coaches.api.urls')),
        path('training/', include('apps.training.api.urls')),
        path('events/', include('apps.events.api.urls')),
        path('city-committee/', include('apps.city_committee.api.urls')),
        path('analytics/', include('apps.analytics.api.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
EOF

# config/asgi.py
cat > config/asgi.py << 'EOF'
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
EOF

# config/wsgi.py
cat > config/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
EOF

# Создаем app_template.py
mkdir -p config
cat > config/app_template << 'EOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

default_app_config = '{{ app_name }}.apps.{{ app_name|title }}Config'
EOF

echo "=== Готово! ==="
echo "Структура проекта создана."
echo "Запустите следующие команды:"
echo "1. chmod +x setup_project.sh"
echo "2. ./setup_project.sh"
echo "3. python manage.py makemigrations"
echo "4. python manage.py migrate"