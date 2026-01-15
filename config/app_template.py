import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

default_app_config = '{{ app_name }}.apps.{{ app_name|title }}Config'
