# Инструкции по настройке внешних сервисов

## Общая информация

Платформа СпортБаш интегрируется с несколькими внешними сервисами для расширения функциональности. Ниже приведены подробные инструкции по настройке каждого сервиса.

---

## 1. Яндекс.Карты API

### Назначение
- Автокомплит при выборе города
- Отображение организаций на карте
- Геокодирование адресов
- Определение координат по адресу

### Шаги настройки

1. **Регистрация в Яндекс.Кабинете**
   - Перейдите на https://developer.tech.yandex.ru/
   - Войдите или зарегистрируйтесь

2. **Создание API ключа**
   - Перейдите в раздел "JavaScript API и HTTP Геокодер"
   - Нажмите "Создать новый ключ"
   - Выберите тип ключа: "JavaScript API и HTTP Геокодер"
   - Укажите домен вашего сайта (например: `sportbash.ru`)
   - Скопируйте полученный API ключ

3. **Настройка в проекте**

   **Вариант 1: Через переменные окружения (рекомендуется)**
   
   Создайте файл `.env` в корне проекта:
   ```env
   YANDEX_MAPS_API_KEY=ваш_api_ключ_здесь
   ```
   
   **Вариант 2: Прямо в settings.py (только для разработки)**
   
   В файле `config/settings/base.py`:
   ```python
   YANDEX_MAPS_API_KEY = 'ваш_api_ключ_здесь'
   ```

4. **Проверка работы**
   - Запустите сервер: `python manage.py runserver`
   - Откройте страницу создания организации
   - В поле "Город" начните вводить название города
   - Должен появиться автокомплит с городами
   - Должна отобразиться карта

### Ограничения
- Бесплатный тариф: до 25,000 запросов в день
- Для продакшена рекомендуется платный тариф

### Использование в коде
```javascript
// API ключ автоматически передаётся в шаблоны через context
window.YANDEX_MAPS_API_KEY = '{{ YANDEX_MAPS_API_KEY }}';

// Инициализация карты
ymaps.ready(function() {
    const map = new ymaps.Map('map', {
        center: [54.7431, 55.9678], // Уфа
        zoom: 10
    });
});
```

---

## 2. Telegram Bot API

### Назначение
- Авторизация через Telegram Mini App
- Отправка уведомлений пользователям
- Интеграция с Telegram Web App

### Шаги настройки

1. **Создание бота**
   - Откройте Telegram и найдите бота @BotFather
   - Отправьте команду `/newbot`
   - Следуйте инструкциям для создания бота
   - Сохраните полученный токен

2. **Настройка Web App**
   - Отправьте команду `/newapp` боту @BotFather
   - Выберите вашего бота
   - Заполните информацию о приложении
   - Укажите URL вашего сайта (например: `https://sportbash.ru`)
   - Получите ссылку на Mini App

3. **Настройка в проекте**

   В файле `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   TELEGRAM_WEBAPP_DOMAIN=https://sportbash.ru
   ```

   В файле `config/settings/auth.py`:
   ```python
   TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
   TELEGRAM_WEBAPP_DOMAIN = os.getenv('TELEGRAM_WEBAPP_DOMAIN', 'https://sportbash.ru')
   ```

4. **Проверка работы**
   - Откройте Mini App в Telegram
   - Попробуйте авторизоваться через Telegram
   - Проверьте, что данные пользователя загружаются

### Безопасность
- Всегда проверяйте `initData` от Telegram на сервере
- Используйте HMAC-SHA-256 для проверки подписи
- Не доверяйте данным, приходящим с клиента

### Пример проверки initData
```python
import hmac
import hashlib
import urllib.parse

def verify_telegram_init_data(init_data, bot_token):
    """Проверка подписи initData от Telegram"""
    parsed_data = dict(urllib.parse.parse_qsl(init_data))
    received_hash = parsed_data.pop('hash', '')
    
    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()
    
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == received_hash
```

---

## 3. ВКонтакте OAuth 2.0

### Назначение
- Авторизация через ВКонтакте
- Получение данных профиля пользователя

### Шаги настройки

1. **Создание приложения**
   - Перейдите на https://vk.com/apps?act=manage
   - Нажмите "Создать приложение"
   - Выберите тип: "Веб-сайт"
   - Заполните название и описание
   - Сохраните `Application ID` и `Secure key`

2. **Настройка OAuth**
   - В настройках приложения перейдите в раздел "Настройки"
   - Укажите "Доверенный redirect URI": `https://sportbash.ru/auth/vk/callback/`
   - Сохраните изменения

3. **Настройка в проекте**

   В файле `.env`:
   ```env
   VK_CLIENT_ID=ваш_application_id
   VK_CLIENT_SECRET=ваш_secure_key
   VK_REDIRECT_URI=https://sportbash.ru/auth/vk/callback/
   ```

   В файле `config/settings/auth.py`:
   ```python
   VK_CLIENT_ID = os.getenv('VK_CLIENT_ID')
   VK_CLIENT_SECRET = os.getenv('VK_CLIENT_SECRET')
   VK_REDIRECT_URI = os.getenv('VK_REDIRECT_URI', 'https://sportbash.ru/auth/vk/callback/')
   ```

4. **Проверка работы**
   - Откройте страницу входа
   - Нажмите "Войти через ВКонтакте"
   - Разрешите доступ приложению
   - Проверьте, что пользователь авторизован

### Права доступа (Scope)
Рекомендуемые права:
- `email` - для получения email пользователя
- `offline` - для долгосрочного доступа

### Пример OAuth flow
```python
# 1. Перенаправление на VK
auth_url = f"https://oauth.vk.com/authorize?client_id={VK_CLIENT_ID}&redirect_uri={VK_REDIRECT_URI}&scope=email&response_type=code"

# 2. Получение access_token
token_url = f"https://oauth.vk.com/access_token?client_id={VK_CLIENT_ID}&client_secret={VK_CLIENT_SECRET}&redirect_uri={VK_REDIRECT_URI}&code={code}"

# 3. Получение данных пользователя
user_url = f"https://api.vk.com/method/users.get?access_token={access_token}&v=5.131"
```

---

## 4. Email (SMTP)

### Назначение
- Отправка уведомлений пользователям
- Восстановление пароля
- Подтверждение регистрации

### Шаги настройки

1. **Выбор SMTP сервера**

   **Вариант 1: Yandex Mail (рекомендуется для РФ)**
   - Создайте почтовый ящик на Yandex
   - Включите "Пароли приложений" в настройках безопасности
   - Создайте пароль для приложения

   **Вариант 2: Gmail**
   - Создайте аккаунт Google
   - Включите двухфакторную аутентификацию
   - Создайте пароль приложения

   **Вариант 3: Собственный SMTP сервер**
   - Настройте SMTP сервер (Postfix, Exim и т.д.)
   - Получите данные для подключения

2. **Настройка в проекте**

   В файле `.env`:
   ```env
   EMAIL_HOST=smtp.yandex.ru
   EMAIL_PORT=465
   EMAIL_USE_SSL=True
   EMAIL_HOST_USER=your-email@yandex.ru
   EMAIL_HOST_PASSWORD=ваш_пароль_приложения
   DEFAULT_FROM_EMAIL=your-email@yandex.ru
   ```

   В файле `config/settings/integrations.py`:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.yandex.ru')
   EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
   EMAIL_USE_SSL = True
   EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
   DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
   ```

3. **Проверка работы**
   ```python
   from django.core.mail import send_mail
   
   send_mail(
       'Тестовое письмо',
       'Это тестовое письмо от СпортБаш',
       'from@example.com',
       ['to@example.com'],
       fail_silently=False,
   )
   ```

### Настройки для популярных провайдеров

**Yandex Mail:**
```
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
```

**Gmail:**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**Mail.ru:**
```
EMAIL_HOST=smtp.mail.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
```

---

## 5. MinIO / S3-совместимое хранилище

### Назначение
- Хранение загруженных файлов (фото, документы)
- Соответствие требованиям ФЗ-152 (хранение в РФ)

### Шаги настройки

1. **Установка MinIO (локально)**
   ```bash
   # Скачайте MinIO с https://min.io/download
   # Запустите сервер
   minio server /path/to/data --console-address ":9001"
   ```

2. **Или использование облачного S3 (Selectel, Yandex Object Storage)**
   - Зарегистрируйтесь у провайдера
   - Создайте bucket (контейнер)
   - Получите Access Key и Secret Key

3. **Установка библиотеки**
   ```bash
   pip install django-storages boto3
   ```

4. **Настройка в проекте**

   В файле `.env`:
   ```env
   MINIO_ENDPOINT=http://localhost:9000
   MINIO_ACCESS_KEY=ваш_access_key
   MINIO_SECRET_KEY=ваш_secret_key
   MINIO_BUCKET_NAME=sportbash-files
   MINIO_SECURE=False
   ```

   В файле `config/settings/integrations.py`:
   ```python
   MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
   MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
   MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
   MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'sportbash-files')
   MINIO_SECURE = os.getenv('MINIO_SECURE', 'False') == 'True'
   ```

   В файле `config/settings/base.py` добавьте:
   ```python
   INSTALLED_APPS = [
       ...
       'storages',
   ]
   
   # Настройки хранилища
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   AWS_ACCESS_KEY_ID = MINIO_ACCESS_KEY
   AWS_SECRET_ACCESS_KEY = MINIO_SECRET_KEY
   AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET_NAME
   AWS_S3_ENDPOINT_URL = MINIO_ENDPOINT
   AWS_S3_USE_SSL = MINIO_SECURE
   ```

5. **Проверка работы**
   - Загрузите файл через интерфейс
   - Проверьте, что файл появился в MinIO/S3
   - Проверьте доступность файла по URL

### Рекомендации
- Для продакшена используйте облачное хранилище в РФ (Selectel, Yandex Object Storage)
- Настройте CORS для доступа к файлам
- Настройте политику доступа (публичные/приватные файлы)

---

## 6. База данных PostgreSQL

### Назначение
- Хранение всех данных системы
- Соответствие требованиям ФЗ-152 (хранение в РФ)

### Шаги настройки

1. **Установка PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # Windows
   # Скачайте установщик с https://www.postgresql.org/download/windows/
   ```

2. **Создание базы данных**
   ```sql
   CREATE DATABASE sport_rb_db;
   CREATE USER sport_rb_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE sport_rb_db TO sport_rb_user;
   ```

3. **Настройка в проекте**

   В файле `.env`:
   ```env
   DB_ENGINE=postgresql
   DB_NAME=sport_rb_db
   DB_USER=sport_rb_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

   В файле `config/settings/base.py`:
   ```python
   DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite')
   
   if DB_ENGINE == 'postgresql':
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.postgresql',
               'NAME': os.getenv('DB_NAME', 'sport_rb_db'),
               'USER': os.getenv('DB_USER', 'postgres'),
               'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
               'HOST': os.getenv('DB_HOST', 'localhost'),
               'PORT': os.getenv('DB_PORT', '5432'),
           }
       }
   ```

4. **Применение миграций**
   ```bash
   python manage.py migrate
   ```

### Рекомендации
- Используйте PostgreSQL 12 или выше
- Настройте регулярные бэкапы
- Используйте connection pooling (PgBouncer)
- Настройте репликацию для высокой доступности

---

## 7. Переменные окружения (.env файл)

### Рекомендуемая структура .env файла

```env
# Django
SECRET_KEY=your-secret-key-must-be-at-least-32-chars-long
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.ru

# База данных
DB_ENGINE=postgresql
DB_NAME=sport_rb_db
DB_USER=sport_rb_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Яндекс.Карты
YANDEX_MAPS_API_KEY=ваш_api_ключ

# Telegram
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_WEBAPP_DOMAIN=https://sportbash.ru

# ВКонтакте
VK_CLIENT_ID=ваш_client_id
VK_CLIENT_SECRET=ваш_client_secret
VK_REDIRECT_URI=https://sportbash.ru/auth/vk/callback/

# Email
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=ваш_пароль_приложения
DEFAULT_FROM_EMAIL=your-email@yandex.ru

# MinIO/S3
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=ваш_access_key
MINIO_SECRET_KEY=ваш_secret_key
MINIO_BUCKET_NAME=sportbash-files
MINIO_SECURE=False

# CORS (для Telegram Mini App)
CORS_ALLOWED_ORIGINS=https://sportbash.ru,https://t.me
```

### Безопасность
- **НИКОГДА** не коммитьте `.env` файл в Git
- Добавьте `.env` в `.gitignore`
- Используйте разные настройки для dev/prod
- Храните секретные ключи в безопасном месте

---

## 8. Проверка всех настроек

### Скрипт проверки

Создайте файл `check_services.py`:

```python
import os
from django.conf import settings

def check_services():
    """Проверка настроек всех внешних сервисов"""
    checks = {
        'Yandex Maps': bool(getattr(settings, 'YANDEX_MAPS_API_KEY', '')),
        'Telegram': bool(getattr(settings, 'TELEGRAM_BOT_TOKEN', '')),
        'VK': bool(getattr(settings, 'VK_CLIENT_ID', '')),
        'Email': bool(getattr(settings, 'EMAIL_HOST_USER', '')),
        'MinIO': bool(getattr(settings, 'MINIO_ACCESS_KEY', '')),
    }
    
    print("Проверка настроек сервисов:")
    for service, configured in checks.items():
        status = "✅ Настроено" if configured else "❌ Не настроено"
        print(f"{service}: {status}")
    
    return all(checks.values())

if __name__ == '__main__':
    import django
    django.setup()
    check_services()
```

Запуск:
```bash
python manage.py shell < check_services.py
```

---

## 9. Troubleshooting

### Проблема: Яндекс.Карты не загружаются
**Решение:**
- Проверьте API ключ в настройках
- Убедитесь, что домен добавлен в список разрешённых
- Проверьте консоль браузера на ошибки

### Проблема: Telegram авторизация не работает
**Решение:**
- Проверьте токен бота
- Убедитесь, что проверка `initData` работает корректно
- Проверьте логи сервера

### Проблема: Email не отправляется
**Решение:**
- Проверьте настройки SMTP
- Убедитесь, что используется пароль приложения (не основной пароль)
- Проверьте firewall и порты

### Проблема: Файлы не загружаются в MinIO
**Решение:**
- Проверьте доступность MinIO сервера
- Убедитесь в правильности Access Key и Secret Key
- Проверьте права доступа к bucket

---

## 10. Рекомендации для продакшена

1. **Используйте переменные окружения** для всех секретных данных
2. **Настройте HTTPS** для всех внешних сервисов
3. **Используйте облачные хранилища в РФ** (Selectel, Yandex Object Storage)
4. **Настройте мониторинг** всех внешних сервисов
5. **Используйте CDN** для статических файлов
6. **Настройте резервное копирование** базы данных
7. **Используйте rate limiting** для API
8. **Настройте логирование** всех внешних запросов
