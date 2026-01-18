# Frontend Application

Веб-интерфейс пользователя для платформы СпортБаш.

## Структура

```
apps/frontend/
├── __init__.py
├── apps.py          # Конфигурация приложения
├── urls.py          # URL маршруты для страниц
├── views.py         # Views для отображения страниц
├── settings.py      # Frontend-специфичные настройки
└── README.md        # Эта документация
```

## Назначение

Приложение `apps/frontend` отвечает за отображение веб-интерфейса пользователя. Оно использует Django Templates и HTMX для создания динамического интерфейса.

## Шаблоны

Шаблоны находятся в `templates/frontend/`:
- `index.html` - Главная страница
- `dashboard.html` - Личный кабинет
- `auth/login.html` - Вход
- `auth/register.html` - Регистрация
- `organizations/list.html` - Список организаций
- `organizations/create.html` - Создание организации
- `events/list.html` - Список мероприятий
- `events/detail.html` - Детали мероприятия

## Статические файлы

Статические файлы находятся в `static/`:
- `css/main.css` - Основные стили (бело-синяя тема)
- `js/main.js` - JavaScript функции и HTMX интеграция

## URL структура

Все страницы доступны под корневым путем:

- `/` - Главная страница
- `/login/` - Вход
- `/register/` - Регистрация
- `/dashboard/` - Личный кабинет
- `/organizations/` - Список организаций
- `/organizations/create/` - Создание организации
- `/events/` - Список мероприятий
- `/events/<id>/` - Детали мероприятия

## Интеграция с API

Frontend взаимодействует с API через:
1. **HTMX** - для динамических обновлений без перезагрузки
2. **Fetch API** - для прямых AJAX запросов
3. **JWT токены** - для аутентификации

Все API запросы идут на `/api/...` endpoints.

## Настройки

Frontend-специфичные настройки находятся в `apps/frontend/settings.py`:
- Название и описание сайта
- Настройки статических файлов
- Интеграции (Telegram, VK)

## Развертывание

### Единый сервер (текущая конфигурация)
Frontend и API работают на одном сервере:
```
http://localhost:8000/      - Frontend
http://localhost:8000/api/   - API
```

### Отдельный Frontend сервер
Для развертывания только Frontend:
1. В `config/urls.py` оставить только:
   ```python
   path('', include('apps.frontend.urls')),
   ```
2. Настроить проксирование API запросов на API сервер
3. Обновить базовый URL API в JavaScript:
   ```javascript
   const API_BASE_URL = 'https://api.sportbash.ru';
   ```

## Технологии

- **Django Templates** - шаблонизация
- **HTMX** - динамические обновления
- **CSS** - стилизация (бело-синяя тема)
- **Vanilla JavaScript** - интерактивность

## Адаптивность

Сайт полностью адаптивен:
- Десктоп (1200px+)
- Планшет (768px - 1199px)
- Мобильные (< 768px)

## Telegram Mini App

Frontend поддерживает работу как Telegram Mini App:
- Автоматическое определение Telegram WebApp API
- Авторизация через Telegram initData
- Адаптация интерфейса под Telegram

## Разработка

Для разработки Frontend:
1. Включите DEBUG режим в настройках
2. Используйте `python manage.py runserver`
3. Статические файлы автоматически подхватываются

## Сборка статики

Для продакшена:
```bash
python manage.py collectstatic
```

Статические файлы будут собраны в `staticfiles/`.
