# config/settings/security.py
from .base import *

# ФЗ-152
PDN_STORAGE_REGION = 'RU'  # Все ПДн в РФ
ENCRYPTION_KEY = SECRET_KEY[:32].encode()  # для AES-256

# 2FA
TWO_FACTOR_ROLES = ['admin_rb', 'moderator', 'committee_staff']
TWO_FACTOR_APP_NAME = 'СпортБаш'

# Удаление данных
DATA_DELETION_RETENTION_DAYS = 30