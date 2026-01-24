# Документация API

## Общая информация

API построено на Django REST Framework (DRF) и предоставляет RESTful интерфейс для всех функций платформы.

**Базовый URL:** `/api/`

**Формат данных:** JSON

**Аутентификация:** 
- Session Authentication (для веб-интерфейса)
- JWT Token Authentication (для мобильных приложений и внешних интеграций)

---

## 1. Аутентификация (`/api/auth/`)

### 1.1. Информация об API
**GET** `/api/auth/`

Возвращает список доступных endpoints для аутентификации.

**Ответ:**
```json
{
  "endpoints": {
    "login": "/api/auth/login/",
    "register": "/api/auth/register/",
    "vk": "/api/auth/vk/",
    "telegram": "/api/auth/telegram/"
  },
  "methods": {
    "login": "POST",
    "register": "POST",
    "vk": "POST",
    "telegram": "POST"
  }
}
```

### 1.2. Вход через Email
**POST** `/api/auth/login/`

**Тело запроса:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Ответ (успех):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов"
  },
  "needs_role_selection": false,
  "active_role": "athlete"
}
```

**Ответ (ошибка):**
```json
{
  "error": "Неверный email или пароль"
}
```

### 1.3. Регистрация
**POST** `/api/auth/register/`

**Тело запроса:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Иван",
  "last_name": "Иванов",
  "patronymic": "Иванович",
  "city": "Уфа"
}
```

**Ответ:**
```json
{
  "success": true,
  "user_id": 1,
  "needs_role_selection": true,
  "message": "Регистрация успешна. Выберите роль в личном кабинете."
}
```

### 1.4. Вход через ВКонтакте
**POST** `/api/auth/vk/`

**Тело запроса:**
```json
{
  "access_token": "vk_access_token",
  "user_id": 123456789
}
```

**Ответ:**
```json
{
  "success": true,
  "user": {...},
  "needs_profile_completion": false,
  "active_role": "athlete"
}
```

### 1.5. Вход через Telegram
**POST** `/api/auth/telegram/`

**Тело запроса:**
```json
{
  "init_data": "query_id=...&user=...&auth_date=...&hash=..."
}
```

**Ответ:**
```json
{
  "success": true,
  "user": {...},
  "needs_profile_completion": false,
  "active_role": "athlete"
}
```

---

## 2. Пользователи (`/api/users/`)

### 2.1. Получить все роли пользователя
**GET** `/api/users/roles/`

**Требуется аутентификация:** Да

**Ответ:**
```json
{
  "roles": [
    {
      "role": "athlete",
      "created_at": "2025-01-01T00:00:00Z",
      "is_active": true
    },
    {
      "role": "coach",
      "created_at": "2025-01-02T00:00:00Z",
      "is_active": false
    }
  ]
}
```

### 2.2. Выбор роли
**POST** `/api/users/select-role/`

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "role": "athlete"
}
```

**Доступные роли:** `athlete`, `coach`

**Ответ:**
```json
{
  "success": true,
  "role": "athlete",
  "needs_profile_completion": false,
  "profile_url": null
}
```

### 2.3. Переключение роли
**POST** `/api/users/switch-role/`

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "role": "coach"
}
```

**Ответ:**
```json
{
  "success": true,
  "active_role": "coach"
}
```

### 2.4. Получить/Обновить общие данные пользователя
**GET/PATCH** `/api/users/basic-data/`

**Требуется аутентификация:** Да

**GET - Получить данные:**
```json
{
  "id": 1,
  "first_name": "Иван",
  "last_name": "Иванов",
  "patronymic": "Иванович",
  "full_name": "Иванов Иван Иванович",
  "email": "user@example.com",
  "birth_date": "2000-01-01",
  "gender": "M",
  "city": "Уфа",
  "city_display": "г. Уфа",
  "photo": null,
  "photo_url": null
}
```

**PATCH - Обновить данные:**
```json
{
  "full_name": "Иванов Иван Иванович",
  "birth_date": "2000-01-01",
  "gender": "M",
  "city": "г. Уфа",
  "photo": "<file>"
}
```

**Примечание:** `full_name` парсится на `first_name`, `last_name`, `patronymic` автоматически.

---

## 3. Организации (`/api/organizations/`)

### 3.1. Список организаций
**GET** `/api/organizations/`

**Параметры запроса:**
- `city` (string) - Фильтр по городу
- `sport` (string) - Фильтр по виду спорта
- `status` (string) - Фильтр по статусу (`approved`, `pending`, `rejected`)

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "ДЮСШ Олимпиец",
    "org_type": "state",
    "city": "Уфа",
    "address": "ул. Спортивная, д. 1",
    "latitude": "54.7431",
    "longitude": "55.9678",
    "website": "https://example.com",
    "sport_directions": ["Футбол", "Баскетбол"]
  }
]
```

### 3.2. Детали организации
**GET** `/api/organizations/<org_id>/`

**Ответ:**
```json
{
  "id": 1,
  "name": "ДЮСШ Олимпиец",
  "org_type": "state",
  "org_type_display": "Государственная",
  "city": "Уфа",
  "address": "ул. Спортивная, д. 1",
  "latitude": "54.7431",
  "longitude": "55.9678",
  "website": "https://example.com",
  "sport_directions": [
    {
      "id": 1,
      "sport_id": 1,
      "sport_name": "Футбол"
    }
  ],
  "groups": [
    {
      "id": 1,
      "name": "Группа начальной подготовки",
      "sport_id": 1,
      "sport": "Футбол",
      "age_level": "6-10 лет",
      "description": "Описание группы",
      "schedules": [
        {
          "weekday": "Понедельник",
          "start_time": "18:00:00",
          "end_time": "19:30:00",
          "location": "Зал 1"
        }
      ]
    }
  ],
  "coaches": [
    {
      "id": 1,
      "full_name": "Петров Петр Петрович",
      "specialization": "Футбол",
      "experience_years": 10,
      "bio": "Опытный тренер"
    }
  ]
}
```

### 3.3. Мои организации
**GET** `/api/organizations/my/`

**Требуется аутентификация:** Да (роль `director` или `organization`)

**Ответ:** Аналогичен списку организаций, но только для текущего пользователя.

### 3.4. Создание организации
**POST** `/api/organizations/create/`

**Требуется аутентификация:** Да

**Тело запроса (multipart/form-data):**
```
name: ДЮСШ Олимпиец
org_type: state
city_id: 1
address: ул. Спортивная, д. 1
latitude: 54.7431
longitude: 55.9678
website: https://example.com (необязательно)
inn: 123456789012
documents: <file> (необязательно)
```

**Ответ:**
```json
{
  "id": 1,
  "name": "ДЮСШ Олимпиец",
  "status": "pending",
  "message": "Организация создана и ожидает модерации"
}
```

### 3.5. Модерация организации
**POST** `/api/organizations/moderate/<org_id>/`

**Требуется аутентификация:** Да (роль `admin_rb` или `moderator`)

**Тело запроса:**
```json
{
  "status": "approved",
  "comment": "Организация одобрена"
}
```

---

## 4. Спортсмены (`/api/athletes/`)

### 4.1. Получить/Обновить профиль спортсмена
**GET/PATCH** `/api/athletes/profile/`

**Требуется аутентификация:** Да (роль `athlete`)

**GET - Получить профиль:**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "full_name": "Иванов Иван Иванович"
  },
  "main_sport": {
    "id": 1,
    "name": "Футбол"
  },
  "additional_sports": [
    {
      "id": 2,
      "name": "Баскетбол"
    }
  ],
  "health_group": "I",
  "medical_info": {
    "health_issues": ["Нет"],
    "allergies": "Нет",
    "health_issues_description": ""
  },
  "goals": ["Соревнования", "ЗОЖ"]
}
```

**PATCH - Обновить профиль:**
```json
{
  "main_sport_id": 1,
  "additional_sports_ids": [2, 3],
  "health_group": "I",
  "medical_info": {
    "health_issues": ["Нет"],
    "allergies": "Пыльца",
    "health_issues_description": "Сезонная аллергия"
  },
  "goals": ["Соревнования"]
}
```

### 4.2. Подать заявку в группу
**POST** `/api/athletes/enrollment/request/`

**Требуется аутентификация:** Да (роль `athlete`)

**Тело запроса:**
```json
{
  "group": 1,
  "message": "Хочу записаться в группу"
}
```

**Ответ:**
```json
{
  "id": 1,
  "status": "pending",
  "message": "Заявка отправлена"
}
```

### 4.3. Подать заявку на секцию
**POST** `/api/athletes/section-enrollment/request/`

**Требуется аутентификация:** Да (роль `athlete`)

**Тело запроса:**
```json
{
  "sport_direction": 1,
  "message": "Хочу записаться на секцию футбола"
}
```

### 4.4. Прогресс спортсмена
**GET** `/api/athletes/progress/`

**Требуется аутентификация:** Да (роль `athlete`)

**Ответ:**
```json
{
  "attendance_stats": {
    "total_sessions": 50,
    "attended": 45,
    "percentage": 90
  },
  "event_stats": {
    "participated": 5,
    "upcoming": 2
  },
  "achievements": [...]
}
```

### 4.5. Запросы от родителей
**GET** `/api/athletes/parent-requests/`

**Требуется аутентификация:** Да (роль `athlete`)

**Ответ:**
```json
[
  {
    "id": 1,
    "parent": {
      "id": 2,
      "full_name": "Родителев Родитель Родителевич"
    },
    "status": "pending_child",
    "requested_by": "parent"
  }
]
```

### 4.6. Подтвердить/Отклонить запрос родителя
**POST** `/api/athletes/parent-requests/<request_id>/confirm/`
**POST** `/api/athletes/parent-requests/<request_id>/reject/`

**Требуется аутентификация:** Да (роль `athlete`)

---

## 5. Тренеры (`/api/coaches/`)

### 5.1. Получить/Обновить профиль тренера
**GET/PATCH** `/api/coaches/profile/`

**Требуется аутентификация:** Да (роль `coach`)

**GET - Получить профиль:**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "full_name": "Тренеров Тренер Тренерович"
  },
  "specialization": {
    "id": 1,
    "name": "Футбол"
  },
  "city": {
    "id": 1,
    "name": "Уфа"
  },
  "experience_years": 10,
  "education": "Высшее",
  "bio": "Опытный тренер"
}
```

**PATCH - Обновить профиль:**
```json
{
  "specialization_id": 1,
  "city_id": 1,
  "experience_years": 10,
  "education": "Высшее",
  "bio": "Обновленная биография"
}
```

### 5.2. Список организаций тренера
**GET** `/api/coaches/organizations/`

**Требуется аутентификация:** Да (роль `coach`)

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "ДЮСШ Олимпиец",
    "status": "active"
  }
]
```

### 5.3. Группы тренера
**GET** `/api/coaches/groups/`

**Требуется аутентификация:** Да (роль `coach`)

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Группа начальной подготовки",
    "organization": {
      "id": 1,
      "name": "ДЮСШ Олимпиец"
    },
    "sport": "Футбол",
    "athletes_count": 15
  }
]
```

### 5.4. Группы в организации
**GET** `/api/coaches/organizations/<org_id>/groups/`

**Требуется аутентификация:** Да (роль `coach`)

### 5.5. Детали группы
**GET** `/api/coaches/groups/<group_id>/`

**Требуется аутентификация:** Да (роль `coach`)

**Ответ:**
```json
{
  "id": 1,
  "name": "Группа начальной подготовки",
  "organization": {...},
  "sport": "Футбол",
  "athletes": [
    {
      "id": 1,
      "full_name": "Иванов Иван",
      "attendance_rate": 90
    }
  ],
  "schedules": [...]
}
```

### 5.6. Свободные организации (для подачи заявки)
**GET** `/api/coaches/free-organizations/`

**Требуется аутентификация:** Да (роль `coach`)

**Параметры запроса:**
- `city` (string) - Фильтр по городу
- `sport` (string) - Фильтр по виду спорта

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "ДЮСШ Олимпиец",
    "city": "Уфа",
    "address": "ул. Спортивная, д. 1",
    "sport_directions": ["Футбол", "Баскетбол"],
    "description": "Описание организации"
  }
]
```

### 5.7. Подать заявку в организацию
**POST** `/api/coaches/clubs/request/`

**Требуется аутентификация:** Да (роль `coach`)

**Тело запроса:**
```json
{
  "organization": 1,
  "specialization_id": 1,
  "age_levels": ["6-10 лет", "11-14 лет"],
  "message": "Хочу работать тренером"
}
```

### 5.8. Приглашения тренера
**GET** `/api/coaches/invitations/`

**Требуется аутентификация:** Да (роль `coach`)

**Ответ:**
```json
[
  {
    "id": 1,
    "organization": {
      "id": 1,
      "name": "ДЮСШ Олимпиец"
    },
    "specialization": "Футбол",
    "age_levels": ["6-10 лет"],
    "message": "Приглашаем вас на работу",
    "status": "pending"
  }
]
```

### 5.9. Принять/Отклонить приглашение
**POST** `/api/coaches/invitations/<invitation_id>/accept/`
**POST** `/api/coaches/invitations/<invitation_id>/reject/`

**Требуется аутентификация:** Да (роль `coach`)

### 5.10. Заявки тренеров (для директора)
**GET** `/api/coaches/requests/`

**Требуется аутентификация:** Да (роль `director`)

**Ответ:**
```json
[
  {
    "id": 1,
    "coach": {
      "id": 1,
      "full_name": "Тренеров Тренер"
    },
    "organization": 1,
    "specialization": "Футбол",
    "status": "pending",
    "message": "Хочу работать"
  }
]
```

### 5.11. Одобрить/Отклонить заявку тренера (для директора)
**POST** `/api/coaches/requests/<request_id>/approve/`
**POST** `/api/coaches/requests/<request_id>/reject/`

**Требуется аутентификация:** Да (роль `director`)

### 5.12. Свободные тренеры (для директора)
**GET** `/api/coaches/free-coaches/`

**Требуется аутентификация:** Да (роль `director`)

**Параметры запроса:**
- `city` (string) - Фильтр по городу
- `sport` (string) - Фильтр по виду спорта

### 5.13. Отправить приглашение тренеру (для директора)
**POST** `/api/coaches/invitations/send/`

**Требуется аутентификация:** Да (роль `director`)

**Тело запроса:**
```json
{
  "coach_id": 1,
  "organization_id": 1,
  "specialization_id": 1,
  "age_levels": ["6-10 лет"],
  "message": "Приглашаем вас на работу"
}
```

### 5.14. Одобрить/Отклонить заявку спортсмена
**POST** `/api/coaches/enrollments/<enrollment_id>/approve/`
**POST** `/api/coaches/enrollments/<enrollment_id>/reject/`

**Требуется аутентификация:** Да (роль `coach`)

---

## 6. Родители (`/api/parents/`)

### 6.1. Запросить связь с ребёнком
**POST** `/api/parents/children/request/`

**Требуется аутентификация:** Да (роль `parent`)

**Тело запроса:**
```json
{
  "role_unique_id": "ABC12345"
}
```

**Ответ:**
```json
{
  "id": 1,
  "status": "pending_child",
  "message": "Запрос отправлен ребёнку на подтверждение"
}
```

### 6.2. Список детей
**GET** `/api/parents/children/`

**Требуется аутентификация:** Да (роль `parent`)

**Ответ:**
```json
[
  {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "role_unique_id": "ABC12345",
    "main_sport": "Футбол",
    "organization": "ДЮСШ Олимпиец"
  }
]
```

### 6.3. Профиль ребёнка
**GET** `/api/parents/children/<child_id>/`

**Требуется аутентификация:** Да (роль `parent`)

**Ответ:**
```json
{
  "id": 1,
  "full_name": "Иванов Иван Иванович",
  "main_sport": "Футбол",
  "attendance_stats": {
    "total_sessions": 50,
    "attended": 45,
    "percentage": 90
  },
  "event_stats": {
    "participated": 5,
    "upcoming": 2
  },
  "achievements": [...]
}
```

### 6.4. Запросы на связь
**GET** `/api/parents/requests/`

**Требуется аутентификация:** Да (роль `parent`)

**Ответ:**
```json
[
  {
    "id": 1,
    "parent": {...},
    "child": {...},
    "status": "pending_child",
    "requested_by": "parent"
  }
]
```

### 6.5. Подтвердить/Отклонить запрос
**POST** `/api/parents/requests/<link_id>/confirm/`
**POST** `/api/parents/requests/<link_id>/reject/`

**Требуется аутентификация:** Да

### 6.6. Получить ID роли родителя
**GET** `/api/parents/my-role-id/`

**Требуется аутентификация:** Да (роль `parent`)

**Ответ:**
```json
{
  "unique_id": "XYZ98765"
}
```

---

## 7. Мероприятия (`/api/events/`)

### 7.1. Список мероприятий
**GET** `/api/events/`

**Параметры запроса:**
- `sport_id` (integer) - Фильтр по виду спорта
- `city` (string) - Фильтр по городу
- `status` (string) - Фильтр по статусу (`published`, `draft`, `completed`)

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Чемпионат Республики Башкортостан по футболу",
    "description": "Описание мероприятия",
    "event_type": "competition",
    "level": "republic",
    "city": "Уфа",
    "venue": "Стадион Динамо",
    "start_date": "2025-02-01T10:00:00Z",
    "end_date": "2025-02-03T18:00:00Z",
    "requires_registration": true,
    "status": "published"
  }
]
```

### 7.2. Детали мероприятия
**GET** `/api/events/<event_id>/`

**Ответ:**
```json
{
  "id": 1,
  "title": "Чемпионат Республики Башкортостан по футболу",
  "description": "Описание мероприятия",
  "event_type": "competition",
  "level": "republic",
  "city": "Уфа",
  "venue": "Стадион Динамо",
  "start_date": "2025-02-01T10:00:00Z",
  "end_date": "2025-02-03T18:00:00Z",
  "age_groups": [
    {
      "min_age": 8,
      "max_age": 12
    }
  ],
  "registrations_count": 50
}
```

### 7.3. Регистрация на мероприятие
**POST** `/api/events/<event_id>/register/`

**Требуется аутентификация:** Да (роль `athlete`)

**Тело запроса:**
```json
{
  "athlete_id": 1
}
```

### 7.4. Доступные спортсмены для регистрации
**GET** `/api/events/<event_id>/athletes/`

**Требуется аутентификация:** Да (роль `coach` или `director`)

**Ответ:**
```json
[
  {
    "id": 1,
    "full_name": "Иванов Иван",
    "age": 12,
    "sport": "Футбол"
  }
]
```

### 7.5. Доступные группы для регистрации
**GET** `/api/events/<event_id>/groups/`

**Требуется аутентификация:** Да (роль `coach` или `director`)

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Группа начальной подготовки",
    "athletes_count": 15,
    "sport": "Футбол"
  }
]
```

### 7.6. Массовая регистрация
**POST** `/api/events/<event_id>/bulk-register/`

**Требуется аутентификация:** Да (роль `coach` или `director`)

**Тело запроса:**
```json
{
  "athletes": [1, 2, 3],
  "groups": [1, 2]
}
```

---

## 8. Посещаемость (`/api/attendance/`)

### 8.1. Причины отсутствия
**GET** `/api/attendance/reasons/`

**Ответ:**
```json
[
  {"id": 1, "name": "Болезнь"},
  {"id": 2, "name": "Отпуск"},
  {"id": 3, "name": "Другое"}
]
```

### 8.2. Отметить посещаемость
**POST** `/api/attendance/mark/`

**Требуется аутентификация:** Да (роль `coach`)

**Тело запроса:**
```json
{
  "athlete_id": 1,
  "group_id": 1,
  "date": "2025-01-22",
  "status": "present",
  "absence_reason_id": null
}
```

**Статусы:** `present`, `absent`, `late`

### 8.3. Посещаемость группы
**GET** `/api/attendance/group/<group_id>/`

**Требуется аутентификация:** Да (роль `coach`)

**Параметры запроса:**
- `date` (string, YYYY-MM-DD) - Дата для фильтрации

**Ответ:**
```json
{
  "group": {
    "id": 1,
    "name": "Группа начальной подготовки"
  },
  "attendance": [
    {
      "athlete": {
        "id": 1,
        "full_name": "Иванов Иван"
      },
      "date": "2025-01-22",
      "status": "present"
    }
  ]
}
```

### 8.4. Статистика посещаемости группы
**GET** `/api/attendance/group/<group_id>/stats/`

**Требуется аутентификация:** Да (роль `coach`)

**Ответ:**
```json
{
  "group": {...},
  "total_sessions": 50,
  "attendance_rate": 85.5,
  "athletes_stats": [
    {
      "athlete": {...},
      "attended": 45,
      "absent": 5,
      "percentage": 90
    }
  ]
}
```

### 8.5. Статистика посещаемости организации
**GET** `/api/attendance/organization/<org_id>/stats/`

**Требуется аутентификация:** Да (роль `director`)

### 8.6. Посещаемость спортсмена
**GET** `/api/attendance/athlete/<athlete_id>/`

**Требуется аутентификация:** Да (роль `athlete` или `parent`)

---

## 9. География (`/api/geography/`)

### 9.1. Список регионов
**GET** `/api/geography/regions/`

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Республика Башкортостан"
  }
]
```

### 9.2. Список городов
**GET** `/api/geography/cities/`

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Уфа",
    "region_name": "Республика Башкортостан",
    "settlement_type": "city",
    "display_name": "г. Уфа"
  },
  {
    "id": 2,
    "name": "Булгаково",
    "region_name": "Республика Башкортостан",
    "settlement_type": "village",
    "display_name": "с. Булгаково"
  }
]
```

### 9.3. Поиск городов (автокомплит)
**GET** `/api/geography/cities/search/?q=Уфа`

**Параметры запроса:**
- `q` (string) - Поисковый запрос (минимум 2 символа)

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Уфа",
    "display_name": "г. Уфа"
  }
]
```

### 9.4. Список районов
**GET** `/api/geography/districts/`

---

## 10. Виды спорта (`/api/sports/`)

### 10.1. Список видов спорта
**GET** `/api/sports/`

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Футбол"
  },
  {
    "id": 2,
    "name": "Баскетбол"
  }
]
```

### 10.2. Категории вида спорта
**GET** `/api/sports/<sport_id>/categories/`

---

## 11. Тренировки (`/api/training/`)

### 11.1. Список групп
**GET** `/api/training/`

**Требуется аутентификация:** Да

### 11.2. Возрастные уровни
**GET** `/api/training/age-levels/`

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "6-10 лет",
    "min_age": 6,
    "max_age": 10
  }
]
```

### 11.3. Создать группу
**POST** `/api/training/create/`

**Требуется аутентификация:** Да (роль `director`)

---

## 12. Файлы (`/api/files/`)

### 12.1. Загрузить файл
**POST** `/api/files/upload/`

**Требуется аутентификация:** Да

**Тело запроса (multipart/form-data):**
```
file: <file>
description: Описание файла (необязательно)
```

### 12.2. Список файлов
**GET** `/api/files/list/`

**Требуется аутентификация:** Да

---

## 13. Достижения (`/api/achievements/`)

### 13.1. Список достижений
**GET** `/api/achievements/achievements/`

**Требуется аутентификация:** Да

### 13.2. Список разрядов
**GET** `/api/achievements/ranks/`

**Требуется аутентификация:** Да

### 13.3. Результаты ГТО
**GET** `/api/achievements/gto/`

**Требуется аутентификация:** Да

---

## 14. Уведомления (`/api/notifications/`)

### 14.1. Список уведомлений
**GET** `/api/notifications/`

**Требуется аутентификация:** Да

**Параметры запроса:**
- `unread_only` (boolean) - Только непрочитанные

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Новое уведомление",
    "message": "Текст уведомления",
    "type": "info",
    "is_read": false,
    "created_at": "2025-01-22T10:00:00Z"
  }
]
```

### 14.2. Отметить уведомление как прочитанное
**POST** `/api/notifications/<notification_id>/read/`

**Требуется аутентификация:** Да

### 14.3. Подписки на уведомления
**GET** `/api/notifications/subscriptions/`

**Требуется аутентификация:** Да

### 14.4. Обновить подписку
**PUT/PATCH** `/api/notifications/subscriptions/<subscription_id>/`

**Требуется аутентификация:** Да

---

## 15. Администратор РБ (`/api/admin-rb/`)

### 15.1. Статистика дашборда
**GET** `/api/admin-rb/stats/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Ответ:**
```json
{
  "total_users": 1000,
  "active_users": 800,
  "total_organizations": 50,
  "pending_organizations": 5,
  "total_events": 100,
  "total_attendance_records": 5000
}
```

### 15.2. Организации на модерации
**GET** `/api/admin-rb/organizations/pending/`

**Требуется аутентификация:** Да (роль `admin_rb`)

### 15.3. Список организаций
**GET** `/api/admin-rb/organizations/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Параметры запроса:**
- `search` (string) - Поиск по названию
- `status` (string) - Фильтр по статусу

### 15.4. Модерация организации
**POST** `/api/admin-rb/organizations/<org_id>/moderate/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Тело запроса:**
```json
{
  "status": "approved",
  "comment": "Организация одобрена"
}
```

### 15.5. Список пользователей
**GET** `/api/admin-rb/users/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Параметры запроса:**
- `search` (string) - Поиск по email/имени
- `role` (string) - Фильтр по роли
- `page` (integer) - Номер страницы
- `page_size` (integer) - Размер страницы

### 15.6. Активировать/Деактивировать пользователя
**POST** `/api/admin-rb/users/<user_id>/toggle-status/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Тело запроса:**
```json
{
  "is_active": false
}
```

### 15.7. Назначить роль
**POST** `/api/admin-rb/roles/assign/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Тело запроса:**
```json
{
  "user_id": 1,
  "role": "moderator"
}
```

**Доступные роли:** `moderator`, `admin_rb`

### 15.8. Системные логи
**GET** `/api/admin-rb/logs/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Параметры запроса:**
- `log_type` (string) - Тип лога (`audit`, `django`)
- `limit` (integer) - Количество записей

**Ответ:**
```json
{
  "audit_logs": [...],
  "django_logs": [...]
}
```

---

## 16. Core (`/api/core/`)

### 16.1. Согласия на обработку ПДн
**GET** `/api/core/consents/`

**Требуется аутентификация:** Да

**Ответ:**
```json
[
  {
    "type": "personal_data",
    "granted": true,
    "granted_at": "2025-01-01T00:00:00Z"
  }
]
```

### 16.2. Обновить согласие
**POST** `/api/core/consents/update/`

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "type": "personal_data",
  "granted": true
}
```

### 16.3. Системные константы
**GET** `/api/core/constants/`

**Ответ:**
```json
{
  "roles": ["athlete", "coach", "parent", "director"],
  "event_types": ["competition", "marathon", "gto_festival"],
  "health_groups": ["I", "II", "III"]
}
```

### 16.4. Health Check
**GET** `/api/core/health/`

**Ответ:**
```json
{
  "status": "ok",
  "timestamp": "2025-01-22T10:00:00Z",
  "database": "connected"
}
```

---

## 17. Аудит (`/api/audit/`)

### 17.1. Логи аудита
**GET** `/api/audit/logs/`

**Требуется аутентификация:** Да (роль `admin_rb`)

**Параметры запроса:**
- `user_id` (integer) - Фильтр по пользователю
- `action` (string) - Фильтр по действию
- `date_from` (string) - Дата начала
- `date_to` (string) - Дата окончания

---

## 18. Аналитика (`/api/analytics/`)

### 18.1. Отчёт по охвату населения
**GET** `/api/analytics/reports/population/`

**Требуется аутентификация:** Да (роль `committee_staff` или `admin_rb`)

### 18.2. Отчёт по спортивной активности
**GET** `/api/analytics/reports/sport-activity/`

**Требуется аутентификация:** Да (роль `committee_staff` или `admin_rb`)

### 18.3. Экспорт в Excel
**GET** `/api/analytics/export/<report_type>/excel/`

**Требуется аутентификация:** Да (роль `committee_staff` или `admin_rb`)

---

## 19. Городской комитет (`/api/city-committee/`)

### 19.1. Обзор города
**GET** `/api/city-committee/overview/`

**Требуется аутентификация:** Да (роль `committee_staff`)

### 19.2. Карта организаций
**GET** `/api/city-committee/map/`

**Требуется аутентификация:** Да (роль `committee_staff`)

### 19.3. Экспорт GIS данных
**GET** `/api/city-committee/gis/export/`

**Требуется аутентификация:** Да (роль `committee_staff`)

---

## Коды ошибок

- `200` - Успешный запрос
- `201` - Ресурс создан
- `400` - Ошибка валидации
- `401` - Требуется аутентификация
- `403` - Доступ запрещён
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера

---

## Примеры использования

### Пример 1: Регистрация и выбор роли

```javascript
// 1. Регистрация
const registerResponse = await fetch('/api/auth/register/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
    first_name: 'Иван',
    last_name: 'Иванов',
    city: 'Уфа'
  })
});

// 2. Вход
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

// 3. Выбор роли
const roleResponse = await fetch('/api/users/select-role/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({role: 'athlete'})
});
```

### Пример 2: Получение списка организаций с фильтрацией

```javascript
const response = await fetch('/api/organizations/?city=Уфа&sport=Футбол');
const organizations = await response.json();
```

### Пример 3: Создание организации

```javascript
const formData = new FormData();
formData.append('name', 'ДЮСШ Олимпиец');
formData.append('org_type', 'state');
formData.append('city_id', '1');
formData.append('address', 'ул. Спортивная, д. 1');
formData.append('latitude', '54.7431');
formData.append('longitude', '55.9678');
formData.append('inn', '123456789012');

const response = await fetch('/api/organizations/create/', {
  method: 'POST',
  headers: {'X-CSRFToken': getCookie('csrftoken')},
  body: formData
});
```

---

## Примечания

1. Все запросы, изменяющие данные (POST, PATCH, PUT, DELETE), требуют CSRF токен в заголовке `X-CSRFToken`
2. Для получения CSRF токена используйте `document.cookie` или функцию `getCookie('csrftoken')`
3. JWT токены используются для мобильных приложений и внешних интеграций
4. Все даты и время в формате ISO 8601 (UTC)
5. Координаты (latitude, longitude) в формате Decimal с точностью до 6 знаков после запятой
