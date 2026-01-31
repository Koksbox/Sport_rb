# Настройка OAuth авторизации (ВКонтакте и Telegram)

## Обзор

Система поддерживает авторизацию через:
- **ВКонтакте** - через OAuth 2.0
- **Telegram** - через Telegram WebApp (Mini App)

## ВКонтакте OAuth

### Процесс авторизации

1. Пользователь нажимает "Войти через ВКонтакте"
2. Редирект на `/api/auth/vk/` → начало OAuth flow
3. Редирект на VK OAuth страницу
4. Пользователь разрешает доступ
5. VK возвращает код на `/api/auth/vk/callback/`
6. Система обменивает код на `access_token`
7. Получает данные пользователя из VK API
8. Создаёт или находит аккаунт по `vk_id`
9. Авторизует пользователя через Django сессии
10. Редирект в личный кабинет

### Настройка

#### 1. Создание приложения ВКонтакте

1. Перейдите на https://vk.com/apps?act=manage
2. Нажмите "Создать приложение"
3. Выберите тип: **"Веб-сайт"**
4. Заполните название и описание
5. Сохраните:
   - **Application ID** (Client ID)
   - **Secure key** (Client Secret)

#### 2. Настройка OAuth

1. В настройках приложения перейдите в раздел "Настройки"
2. Укажите "Доверенный redirect URI":
   - **Для разработки:** `http://127.0.0.1:8060/api/auth/vk/callback/`
   - **Для production:** `https://sportbash.ru/api/auth/vk/callback/`

#### 3. Настройка в проекте

В файле `.env`:
```env
VK_CLIENT_ID=ваш_application_id
VK_CLIENT_SECRET=ваш_secure_key
VK_REDIRECT_URI=http://127.0.0.1:8060/api/auth/vk/callback/  # Для разработки
```

Настройки автоматически загружаются из `config/settings/auth.py`.

#### 4. Права доступа (Scope)

Рекомендуемые права:
- `email` - для получения email пользователя

### API Endpoints

- `GET /api/auth/vk/` - Начало OAuth flow (редирект на VK)
- `GET /api/auth/vk/callback/` - Callback от VK (обработка кода)
- `POST /api/auth/vk/token/` - Прямая авторизация по токену (для обратной совместимости)

### Безопасность

- Используется `state` параметр для защиты от CSRF
- State сохраняется в сессии и проверяется в callback
- Все ошибки обрабатываются и показываются пользователю

---

## Telegram WebApp

### Процесс авторизации

1. Пользователь открывает Mini App в Telegram
2. Telegram передаёт `initData` в приложение
3. Система проверяет подпись `initData` (HMAC-SHA-256)
4. Извлекает данные пользователя (`user_id`, `username`, etc.)
5. Создаёт или находит аккаунт по `telegram_id`
6. Авторизует пользователя
7. Редирект в личный кабинет

### Настройка

#### 1. Создание Telegram бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните **токен бота**

#### 2. Настройка WebApp

1. Отправьте `/newapp` в [@BotFather](https://t.me/BotFather)
2. Выберите вашего бота
3. Заполните данные приложения
4. Укажите URL вашего сайта

#### 3. Настройка в проекте

В файле `.env`:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_WEBAPP_DOMAIN=https://sportbash.ru  # Для production
```

### API Endpoints

- `POST /api/auth/telegram/` - Авторизация через Telegram initData

### Формат запроса

```json
{
  "init_data": "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladislav%22%2C%22last_name%22%3A%22Kibenko%22%2C%22username%22%3A%22vdkfrost%22%2C%22language_code%22%3A%22ru%22%7D&auth_date=1662771648&hash=c501b71e775f74ce10e377dea85a7c24cd0f8dd0d0e3e66a57cd99ef9ce5f695"
}
```

### Безопасность

- Проверка HMAC-SHA-256 подписи
- Валидация `auth_date` (не старше 24 часов)
- Проверка домена

### Использование на фронтенде

```javascript
if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp;
    const initData = tg.initData;
    
    fetch('/api/auth/telegram/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ init_data: initData })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.access) {
            // JWT авторизация
            SportBash.saveToken(data.access, data.refresh);
            window.location.href = '/dashboard/';
        }
    });
}
```

---

## Общие особенности

### Автоматическое создание аккаунта

При первом входе через соцсеть:
- Автоматически создаётся аккаунт `CustomUser`
- Привязывается провайдер (`AuthProvider`)
- Создаётся согласие на обработку ПДн (`Consent`)
- Пользователь должен выбрать роль в личном кабинете

### Привязка к существующему аккаунту

Если пользователь уже зарегистрирован через email:
- При входе через соцсеть система ищет аккаунт по `vk_id` или `telegram_id`
- Если аккаунт не найден, создаётся новый
- В будущем можно добавить привязку по email

### Обновление данных

При повторном входе:
- Обновляются имя и фамилия, если они отсутствуют
- Email обновляется, если был получен от VK

---

## Примеры использования

### ВКонтакте

**Начало авторизации:**
```javascript
window.location.href = '/api/auth/vk/';
```

**Обработка ошибок:**
```javascript
// Ошибки передаются через query параметры в URL
// /login/?error=vk_auth_error&error_description=...
```

### Telegram

**Проверка доступности:**
```javascript
if (window.Telegram && window.Telegram.WebApp) {
    // Telegram Mini App доступен
    const tg = window.Telegram.WebApp;
    tg.ready(); // Инициализация
    tg.expand(); // Развернуть на весь экран
}
```

---

## Отладка

### ВКонтакте

1. Проверьте, что `VK_CLIENT_ID` и `VK_CLIENT_SECRET` установлены
2. Убедитесь, что redirect URI совпадает в настройках VK и в проекте
3. Проверьте логи Django на наличие ошибок

### Telegram

1. Проверьте, что `TELEGRAM_BOT_TOKEN` установлен
2. Убедитесь, что бот создан и WebApp настроен
3. Проверьте, что `initData` передаётся корректно
4. Проверьте логи Django на наличие ошибок валидации

---

## Безопасность

### Рекомендации

1. **Никогда не коммитьте** токены и секреты в Git
2. Используйте разные настройки для dev/prod
3. Регулярно обновляйте токены
4. Мониторьте логи на подозрительную активность
5. Используйте HTTPS в production

### Защита от атак

- **CSRF:** Используется `state` параметр для VK OAuth
- **Подделка данных:** Проверка подписи для Telegram
- **Replay атаки:** Валидация `auth_date` для Telegram
