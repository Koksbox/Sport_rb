# config/settings.py
import os
from pathlib import Path

# Загружаем .env ДО всего остального
from dotenv import load_dotenv
load_dotenv()

# Определяем окружение
env = os.getenv('DJANGO_ENV', 'dev')

# Импортируем нужный файл
if env == 'prod':
    from .settings.prod import *
elif env == 'dev':
    from .settings.dev import *
else:
    from .settings.base import *