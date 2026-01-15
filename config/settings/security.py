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
