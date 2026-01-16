# config/settings/dev.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Добавляем консольный вывод в логи
LOGGING['handlers']['console'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatter': 'verbose',
}

# Добавляем 'console' в обработчики Django
if 'console' not in LOGGING['loggers']['django']['handlers']:
    LOGGING['loggers']['django']['handlers'].append('console')