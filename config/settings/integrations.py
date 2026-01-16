# config/settings/integrations.py
from .base import *

# MinIO / S3
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http:152.114.192.9:2007')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'sportbash-files')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'False') == 'True'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.yandex.ru')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER