# API Application

Централизованное приложение для всех API endpoints проекта СпортБаш.

## Структура

```
apps/api/
├── __init__.py
├── apps.py          # Конфигурация приложения
├── urls.py          # Централизованный роутер для всех API
├── settings.py      # API-специфичные настройки
└── README.md        # Эта документация
```

## Назначение

Приложение `apps/api` служит централизованным роутером для всех API endpoints проекта. Оно не содержит бизнес-логику, а только маршрутизирует запросы к соответствующим модулям.

## URL структура

Все API endpoints доступны под префиксом `/api/`:

- `/api/auth/` - Аутентификация
- `/api/users/` - Управление пользователями
- `/api/organizations/` - Спортивные организации
- `/api/athletes/` - Спортсмены
- `/api/parents/` - Родители
- `/api/coaches/` - Тренеры
- `/api/events/` - Мероприятия
- `/api/training/` - Тренировки и группы
- `/api/geography/` - География (города, районы)
- `/api/sports/` - Виды спорта
- `/api/achievements/` - Достижения
- `/api/analytics/` - Аналитика
- `/api/notifications/` - Уведомления
- `/api/core/` - Системные endpoints (health check, константы)
- И другие...

## Интеграция с модулями

Каждый модуль проекта (например, `apps.organizations`) содержит свою папку `api/` с:
- `views.py` - API views
- `urls.py` - URL маршруты модуля
- `serializers.py` - DRF сериализаторы

Приложение `apps.api` подключает эти маршруты через `include()`.

## Настройки

API-специфичные настройки находятся в `apps/api/settings.py`:
- Версия API
- CORS настройки
- DRF конфигурация
- Пагинация

## Развертывание

### Единый сервер (текущая конфигурация)
API и Frontend работают на одном сервере:
```
http://localhost:8000/api/  - API
http://localhost:8000/      - Frontend
```

### Отдельный API сервер
Для развертывания только API:
1. В `config/urls.py` оставить только:
   ```python
   path('api/', include('apps.api.urls')),
   ```
2. Настроить CORS для доступа с Frontend сервера
3. Настроить аутентификацию (JWT токены)

## Документация API

Для генерации документации API рекомендуется использовать:
- **drf-yasg** (Swagger/OpenAPI)
- **django-rest-framework** встроенная документация

## Тестирование

Проверка работоспособности API:
```bash
# Health check
curl http://localhost:8000/api/core/health/

# Список организаций (требует аутентификации)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/organizations/
```

## Версионирование

В будущем можно добавить версионирование API:
```python
# apps/api/urls.py
urlpatterns = [
    path('v1/', include('apps.api.v1.urls')),
    path('v2/', include('apps.api.v2.urls')),
]
```
