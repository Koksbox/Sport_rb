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
