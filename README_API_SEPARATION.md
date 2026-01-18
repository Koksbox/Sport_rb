# Разделение API и Frontend

Проект разделен на два отдельных приложения:

## Структура

### 1. `apps/api` - API приложение
Централизованное приложение для всех API endpoints.

**Расположение:** `apps/api/`

**Файлы:**
- `urls.py` - централизованный роутер для всех API endpoints
- `settings.py` - специфичные настройки для API
- `apps.py` - конфигурация приложения

**URL префикс:** `/api/`

**Все API endpoints доступны под:**
- `/api/auth/` - аутентификация
- `/api/users/` - пользователи
- `/api/organizations/` - организации
- `/api/events/` - мероприятия
- И т.д.

### 2. `apps/frontend` - Frontend приложение
Приложение для веб-интерфейса пользователя.

**Расположение:** `apps/frontend/`

**Файлы:**
- `views.py` - views для отображения страниц
- `urls.py` - маршруты для фронтенда
- `settings.py` - специфичные настройки для фронтенда
- `apps.py` - конфигурация приложения

**URL префикс:** `/` (корневой путь)

**Страницы:**
- `/` - главная страница
- `/login/` - вход
- `/register/` - регистрация
- `/dashboard/` - личный кабинет
- `/organizations/` - список организаций
- `/events/` - список мероприятий
- И т.д.

## Архитектура

```
config/
├── urls.py              # Главный роутер
│   ├── /api/ → apps.api.urls
│   └── / → apps.frontend.urls
│
apps/
├── api/                 # API приложение
│   ├── urls.py         # Централизованный API роутер
│   └── settings.py     # API настройки
│
├── frontend/            # Frontend приложение
│   ├── urls.py         # Frontend маршруты
│   ├── views.py        # Frontend views
│   └── settings.py     # Frontend настройки
│
└── [другие приложения]  # Бизнес-логика
    └── api/            # API endpoints каждого модуля
```

## Преимущества разделения

1. **Четкое разделение ответственности**
   - API и Frontend логически разделены
   - Легче поддерживать и развивать

2. **Масштабируемость**
   - API можно легко вынести на отдельный сервер
   - Frontend можно заменить на SPA (React/Vue) без изменения API

3. **Гибкость развертывания**
   - API и Frontend можно деплоить отдельно
   - Разные настройки для разных окружений

4. **Упрощение разработки**
   - Разные команды могут работать над API и Frontend независимо
   - Четкие границы между компонентами

## Миграция на отдельные серверы

### Вариант 1: API на отдельном домене

**API сервер:** `https://api.sportbash.ru`
**Frontend сервер:** `https://sportbash.ru`

Настройки для Frontend:
```python
# config/settings/frontend.py
API_BASE_URL = 'https://api.sportbash.ru'
```

### Вариант 2: API на поддомене

**API:** `https://sportbash.ru/api/`
**Frontend:** `https://sportbash.ru/`

Текущая конфигурация уже поддерживает это.

## Настройки

### API настройки (`apps/api/settings.py`)
- Версия API
- CORS настройки
- DRF конфигурация
- Пагинация

### Frontend настройки (`apps/frontend/settings.py`)
- Название и описание сайта
- Настройки статических файлов
- Интеграции (Telegram, VK)

## Развертывание

### Раздельное развертывание

1. **API сервер:**
```bash
# Настроить только API endpoints
# В config/urls.py оставить только:
path('api/', include('apps.api.urls')),
```

2. **Frontend сервер:**
```bash
# Настроить только Frontend
# В config/urls.py оставить только:
path('', include('apps.frontend.urls')),
# И настроить проксирование API запросов на API сервер
```

### Единое развертывание (текущее)

Оба приложения работают на одном сервере:
```python
# config/urls.py
urlpatterns = [
    path('api/', include('apps.api.urls')),      # API
    path('', include('apps.frontend.urls')),      # Frontend
]
```

## Тестирование

### Проверка API
```bash
curl http://localhost:8000/api/core/health/
```

### Проверка Frontend
```bash
curl http://localhost:8000/
```

## Дальнейшее развитие

1. **Добавить версионирование API:**
   - `/api/v1/` для текущей версии
   - `/api/v2/` для будущих версий

2. **Добавить API документацию:**
   - Swagger/OpenAPI
   - ReDoc

3. **Оптимизация:**
   - Кэширование для API
   - CDN для статики Frontend
