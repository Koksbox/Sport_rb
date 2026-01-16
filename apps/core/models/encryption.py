from django.db import models
from cryptography.fernet import Fernet
import os

FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY must be set in environment")

fernet = Fernet(FERNET_KEY.encode())

class EncryptedTextField(models.TextField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return fernet.decrypt(value.encode()).decode()
        except Exception:
            return value

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        return fernet.encrypt(value.encode()).decode()