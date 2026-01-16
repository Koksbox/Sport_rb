# apps/core/models/encryption.py
from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
import base64

class EncryptedFieldMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fernet = Fernet(base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode()))

    def to_python(self, value):
        if value is None or not isinstance(value, str):
            return value
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except Exception:
            return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return self._fernet.encrypt(str(value).encode()).decode()

class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    pass