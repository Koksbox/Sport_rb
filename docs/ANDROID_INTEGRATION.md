# Документация по интеграции Android приложения

## 📱 Общая архитектура

### Технологический стек
- **Backend**: Django REST Framework (DRF)
- **Аутентификация**: JWT (JSON Web Tokens) через `rest_framework_simplejwt`
- **Формат данных**: JSON
- **Базовый URL**: `https://yourdomain.ru/api/`

---

## 🔐 Аутентификация

### 1. Регистрация пользователя

**Endpoint**: `POST /api/auth/register/`

**Запрос**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "password2": "SecurePassword123!",
  "first_name": "Иван",
  "last_name": "Иванов",
  "patronymic": "Иванович",
  "phone": "+79191234567",
  "city": "Уфа"
}
```

**Ответ (успех)**:
```json
{
  "message": "Регистрация успешна! Выберите роль в личном кабинете.",
  "user_id": 1,
  "email": "user@example.com",
  "needs_role_selection": true
}
```

**Ответ (ошибка)**:
```json
{
  "email": ["Пользователь с таким email уже существует"],
  "password": ["Пароль слишком простой"]
}
```

### 2. Вход в систему

**Endpoint**: `POST /api/auth/login/`

**Запрос**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Ответ (успех)**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
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

### 3. Обновление токена

**Endpoint**: `POST /api/auth/token/refresh/`

**Запрос**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Ответ**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Вход через Telegram

**Endpoint**: `POST /api/auth/telegram/`

**Запрос**:
```json
{
  "init_data": "user=%7B%22id%22%3A123456789..."
}
```

**Ответ**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "needs_profile_completion": true,
  "needs_role_selection": false
}
```

### 5. Вход через ВКонтакте

**Endpoint**: `POST /api/auth/vk/`

**Запрос**:
```json
{
  "access_token": "vk_access_token_here"
}
```

**Ответ**: Аналогично входу через email

---

## 👤 Управление ролями

### 1. Получить все роли пользователя

**Endpoint**: `GET /api/users/roles/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
{
  "roles": [
    {
      "role": "athlete",
      "role_name": "Спортсмен",
      "unique_id": "ABC12345",
      "created_at": "2024-01-15T10:30:00Z",
      "is_active": true
    },
    {
      "role": "coach",
      "role_name": "Тренер",
      "unique_id": "XYZ67890",
      "created_at": "2024-01-20T14:20:00Z",
      "is_active": false
    }
  ]
}
```

### 2. Выбор/создание роли

**Endpoint**: `POST /api/users/select-role/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Запрос (для спортсмена)**:
```json
{
  "role": "athlete",
  "city": "Уфа",
  "sport_id": 1,
  "birth_date": "2010-05-15"
}
```

**Запрос (для тренера)**:
```json
{
  "role": "coach",
  "city_coach": "Уфа",
  "specialization_id": 1,
  "experience_years": 5
}
```

**Ответ**:
```json
{
  "message": "Роль 'athlete' успешно выбрана.",
  "role": "athlete",
  "needs_profile_completion": false,
  "profile_url": null,
  "redirect_to": "/dashboard/"
}
```

### 3. Переключение между ролями

**Endpoint**: `POST /api/users/switch-role/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Запрос**:
```json
{
  "role": "coach"
}
```

**Ответ**:
```json
{
  "success": true,
  "role": "coach"
}
```

### 4. Получить ID активной роли

**Endpoint**: `GET /api/users/role-id/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
{
  "role": "athlete",
  "unique_id": "ABC12345",
  "role_name": "Спортсмен"
}
```

---

## 🏃 Профиль спортсмена

### 1. Получить профиль спортсмена

**Endpoint**: `GET /api/athletes/profile/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "patronymic": "Иванович",
    "birth_date": "2010-05-15",
    "phone": "+79191234567",
    "city": "Уфа",
    "photo_url": "/media/photos/user_1.jpg"
  },
  "city": {
    "id": 1,
    "name": "Уфа",
    "region": "Республика Башкортостан"
  },
  "main_sport": {
    "id": 1,
    "name": "Футбол"
  },
  "school_or_university": "Школа №1",
  "health_group": "I",
  "goals": ["ЗОЖ", "Соревнования"]
}
```

### 2. Обновить профиль спортсмена

**Endpoint**: `PUT /api/athletes/profile/`

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Запрос**:
```json
{
  "school_or_university": "Школа №2",
  "health_group": "II",
  "goals": ["ЗОЖ", "Соревнования", "ГТО"],
  "medical_restrictions": ["Астма"],
  "allergies": "Нет",
  "emergency_contact_name": "Иванова Мария Петровна",
  "emergency_contact_phone": "+79191234568"
}
```

### 3. Получить прогресс спортсмена

**Endpoint**: `GET /api/athletes/progress/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
{
  "attendance": {
    "2024-01": 15,
    "2024-02": 18,
    "2024-03": 20
  },
  "events": [
    {
      "id": 1,
      "name": "Чемпионат города",
      "date": "2024-03-15",
      "result": "1 место"
    }
  ],
  "achievements": [
    {
      "id": 1,
      "title": "Лучший игрок месяца",
      "date": "2024-02-28"
    }
  ]
}
```

---

## 🏢 Организации

### 1. Список организаций

**Endpoint**: `GET /api/organizations/`

**Query параметры**:
- `city` - фильтр по городу
- `sport` - фильтр по виду спорта

**Ответ**:
```json
[
  {
    "id": 1,
    "name": "ДЮСШ №1",
    "org_type": "state",
    "city": "Уфа",
    "address": "ул. Ленина, 1",
    "latitude": "54.7351",
    "longitude": "55.9587",
    "website": "https://example.com",
    "sports": ["Футбол", "Баскетбол"]
  }
]
```

### 2. Детали организации

**Endpoint**: `GET /api/organizations/{org_id}/`

**Ответ**:
```json
{
  "id": 1,
  "name": "ДЮСШ №1",
  "org_type": "state",
  "city": "Уфа",
  "address": "ул. Ленина, 1",
  "latitude": "54.7351",
  "longitude": "55.9587",
  "website": "https://example.com",
  "sports": ["Футбол", "Баскетбол"],
  "groups": [
    {
      "id": 1,
      "name": "Группа начальной подготовки",
      "sport": "Футбол",
      "coach": "Петров Иван Сергеевич",
      "schedule": "Пн, Ср, Пт 18:00-19:30"
    }
  ]
}
```

### 3. Создание организации

**Endpoint**: `POST /api/organizations/create/`

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Запрос** (FormData):
```
name: ДЮСШ №1
org_type: state
city_id: 1
address: ул. Ленина, 1
latitude: 54.7351
longitude: 55.9587
website: https://example.com
inn: 1234567890
documents[0][doc_type]: license
documents[0][file_path]: [файл]
documents[1][doc_type]: charter
documents[1][file_path]: [файл]
```

**Ответ**:
```json
{
  "id": 1,
  "name": "ДЮСШ №1",
  "status": "pending",
  "message": "Организация создана и ожидает модерации"
}
```

---

## 📅 Мероприятия

### 1. Список мероприятий

**Endpoint**: `GET /api/events/`

**Query параметры**:
- `status` - фильтр по статусу (published, draft, completed)
- `sport` - фильтр по виду спорта
- `city` - фильтр по городу

**Ответ**:
```json
[
  {
    "id": 1,
    "name": "Чемпионат города по футболу",
    "description": "Ежегодный чемпионат",
    "start_date": "2024-05-15T10:00:00Z",
    "end_date": "2024-05-20T18:00:00Z",
    "location": "Стадион Центральный",
    "city": "Уфа",
    "sport": "Футбол",
    "age_groups": [
      {
        "min_age": 10,
        "max_age": 12
      }
    ],
    "registration_open": true,
    "is_registered": false
  }
]
```

### 2. Детали мероприятия

**Endpoint**: `GET /api/events/{event_id}/`

**Ответ**:
```json
{
  "id": 1,
  "name": "Чемпионат города по футболу",
  "description": "Ежегодный чемпионат",
  "start_date": "2024-05-15T10:00:00Z",
  "end_date": "2024-05-20T18:00:00Z",
  "location": "Стадион Центральный",
  "city": "Уфа",
  "sport": "Футбол",
  "age_groups": [
    {
      "min_age": 10,
      "max_age": 12
    }
  ],
  "registration_open": true,
  "is_registered": false,
  "participants_count": 45,
  "max_participants": 100
}
```

### 3. Регистрация на мероприятие

**Endpoint**: `POST /api/events/{event_id}/register/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ (успех)**:
```json
{
  "message": "Регистрация успешна!",
  "registration_id": 123
}
```

**Ответ (ошибка)**:
```json
{
  "error": "Возраст не соответствует требованиям. Ваш возраст: 9 лет. Требуемый возраст: 10-12 лет"
}
```

### 4. Отмена регистрации

**Endpoint**: `POST /api/events/{event_id}/cancel/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
{
  "message": "Регистрация отменена"
}
```

### 5. Мои мероприятия

**Endpoint**: `GET /api/events/my/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
[
  {
    "id": 1,
    "name": "Чемпионат города по футболу",
    "start_date": "2024-05-15T10:00:00Z",
    "status": "registered",
    "registration_date": "2024-04-01T12:00:00Z"
  }
]
```

---

## 🏋️ Тренер

### 1. Получить организации тренера

**Endpoint**: `GET /api/coaches/organizations/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
[
  {
    "id": 1,
    "name": "ДЮСШ №1",
    "city_name": "Уфа",
    "sport_name": "Футбол",
    "role": "coach"
  }
]
```

### 2. Получить группы тренера

**Endpoint**: `GET /api/coaches/groups/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
[
  {
    "id": 1,
    "name": "Группа начальной подготовки",
    "organization_name": "ДЮСШ №1",
    "sport_name": "Футбол",
    "enrollments": [
      {
        "id": 1,
        "athlete": {
          "id": 1,
          "full_name": "Иванов Иван Иванович",
          "birth_date": "2010-05-15"
        },
        "status": "active",
        "enrolled_at": "2024-01-15T10:00:00Z"
      }
    ]
  }
]
```

### 3. Отметить посещаемость

**Endpoint**: `POST /api/attendance/mark/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Запрос**:
```json
{
  "group_id": 1,
  "athlete_id": 1,
  "date": "2024-03-15",
  "status": "present",
  "notes": "Отличная тренировка"
}
```

**Ответ**:
```json
{
  "id": 123,
  "message": "Посещаемость отмечена"
}
```

---

## 📊 Виды спорта

### 1. Список видов спорта

**Endpoint**: `GET /api/sports/`

**Ответ**:
```json
[
  {
    "id": 1,
    "name": "Футбол",
    "category": "Командные"
  },
  {
    "id": 2,
    "name": "Баскетбол",
    "category": "Командные"
  }
]
```

---

## 🌍 География

### 1. Список городов

**Endpoint**: `GET /api/geography/cities/`

**Query параметры**:
- `region` - фильтр по региону

**Ответ**:
```json
[
  {
    "id": 1,
    "name": "Уфа",
    "region": "Республика Башкортостан"
  }
]
```

---

## 🔔 Уведомления

### 1. Получить уведомления

**Endpoint**: `GET /api/notifications/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Query параметры**:
- `unread_only` - только непрочитанные (true/false)

**Ответ**:
```json
[
  {
    "id": 1,
    "type": "event_registration",
    "title": "Регистрация на мероприятие",
    "message": "Вы успешно зарегистрированы на мероприятие 'Чемпионат города'",
    "is_read": false,
    "created_at": "2024-03-15T10:00:00Z",
    "data": {
      "event_id": 1,
      "event_name": "Чемпионат города"
    }
  }
]
```

### 2. Отметить уведомление как прочитанное

**Endpoint**: `POST /api/notifications/{notification_id}/read/`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Ответ**:
```json
{
  "message": "Уведомление отмечено как прочитанное"
}
```

---

## 📝 Обратная связь

### 1. Отправить сообщение

**Endpoint**: `POST /api/core/contact/`

**Запрос**:
```json
{
  "name": "Иван Иванов",
  "email": "user@example.com",
  "phone": "+79191234567",
  "subject": "technical",
  "message": "Обнаружил ошибку в приложении",
  "role_id": "ABC12345"
}
```

**Ответ**:
```json
{
  "message": "Сообщение успешно отправлено",
  "id": 123
}
```

---

## ⚠️ Обработка ошибок

### Стандартные HTTP статусы

- `200 OK` - успешный запрос
- `201 Created` - ресурс создан
- `400 Bad Request` - ошибка валидации
- `401 Unauthorized` - требуется аутентификация
- `403 Forbidden` - недостаточно прав
- `404 Not Found` - ресурс не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

### Формат ошибок

**Валидация**:
```json
{
  "email": ["Пользователь с таким email уже существует"],
  "password": ["Пароль слишком простой"]
}
```

**Общая ошибка**:
```json
{
  "error": "Описание ошибки"
}
```

**Ошибка с деталями**:
```json
{
  "error": "Ошибка при создании профиля",
  "details": {
    "field": "sport_id",
    "message": "Вид спорта не найден"
  }
}
```

---

## 🔄 Управление токенами

### Рекомендуемая логика

1. **Сохранение токенов**:
   - Сохранять `access_token` и `refresh_token` в `SharedPreferences` или `EncryptedSharedPreferences`
   - Использовать `refresh_token` для обновления `access_token` перед истечением срока

2. **Обновление токена**:
   - Проверять срок действия `access_token` перед каждым запросом
   - Если токен истек, автоматически обновлять через `refresh_token`
   - Если `refresh_token` истек, перенаправлять на экран входа

3. **Интерцептор для Retrofit/OkHttp**:
   ```kotlin
   class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {
       override fun intercept(chain: Interceptor.Chain): Response {
           val request = chain.request().newBuilder()
               .addHeader("Authorization", "Bearer ${tokenManager.getAccessToken()}")
               .build()
           
           var response = chain.proceed(request)
           
           // Если токен истек, обновляем и повторяем запрос
           if (response.code == 401) {
               val newToken = tokenManager.refreshToken()
               if (newToken != null) {
                   val newRequest = request.newBuilder()
                       .header("Authorization", "Bearer $newToken")
                       .build()
                   response = chain.proceed(newRequest)
               }
           }
           
           return response
       }
   }
   ```

---

## 📱 Рекомендации по реализации на Android

### 1. Архитектура

**Рекомендуется использовать**:
- **MVVM** (Model-View-ViewModel)
- **Repository Pattern** для работы с API
- **Retrofit** для HTTP запросов
- **Room** для локального кэширования
- **Coroutines** или **RxJava** для асинхронности

### 2. Структура пакетов

```
com.sportbash.app
├── data
│   ├── api
│   │   ├── AuthApi
│   │   ├── UserApi
│   │   ├── EventApi
│   │   └── OrganizationApi
│   ├── repository
│   │   ├── AuthRepository
│   │   ├── UserRepository
│   │   └── EventRepository
│   └── local
│       ├── TokenManager
│       └── AppDatabase
├── domain
│   ├── model
│   └── usecase
└── ui
    ├── auth
    ├── profile
    ├── events
    └── organizations
```

### 3. Пример реализации API сервиса

```kotlin
interface AuthApi {
    @POST("auth/register/")
    suspend fun register(@Body request: RegisterRequest): Response<RegisterResponse>
    
    @POST("auth/login/")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
    
    @POST("auth/token/refresh/")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<RefreshTokenResponse>
}
```

### 4. Пример Repository

```kotlin
class AuthRepository(
    private val api: AuthApi,
    private val tokenManager: TokenManager
) {
    suspend fun login(email: String, password: String): Result<LoginResponse> {
        return try {
            val response = api.login(LoginRequest(email, password))
            if (response.isSuccessful) {
                response.body()?.let {
                    tokenManager.saveTokens(it.access, it.refresh)
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception("Login failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### 5. Обработка ошибок

```kotlin
sealed class ApiResult<out T> {
    data class Success<out T>(val data: T) : ApiResult<T>()
    data class Error(val message: String, val code: Int) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}

fun <T> handleApiResponse(response: Response<T>): ApiResult<T> {
    return if (response.isSuccessful) {
        response.body()?.let { ApiResult.Success(it) }
            ?: ApiResult.Error("Empty response", response.code())
    } else {
        val errorBody = response.errorBody()?.string()
        ApiResult.Error(errorBody ?: "Unknown error", response.code())
    }
}
```

---

## 🔒 Безопасность

### 1. Хранение токенов

- Использовать `EncryptedSharedPreferences` для хранения токенов
- Никогда не логировать токены
- Очищать токены при выходе из приложения

### 2. SSL Pinning

- Настроить SSL Pinning для production
- Использовать сертификаты для проверки подлинности сервера

### 3. Валидация данных

- Валидировать все данные на клиенте перед отправкой
- Не доверять данным с сервера без проверки

---

## 📊 Кэширование

### Рекомендации

1. **Кэшировать**:
   - Список видов спорта
   - Список городов
   - Профиль пользователя
   - Список организаций (с TTL)

2. **Не кэшировать**:
   - Уведомления
   - Посещаемость
   - Регистрации на мероприятия

---

## 🔄 Синхронизация данных

### Стратегия

1. **Офлайн режим**:
   - Сохранять последние данные в локальной БД
   - Показывать кэшированные данные при отсутствии интернета
   - Синхронизировать при восстановлении соединения

2. **Фоновая синхронизация**:
   - Использовать WorkManager для периодической синхронизации
   - Синхронизировать уведомления каждые 5-10 минут
   - Синхронизировать профиль при открытии приложения

---

## 📝 Дополнительные рекомендации

1. **Логирование**:
   - Логировать все API запросы в debug режиме
   - Не логировать токены и пароли
   - Отправлять критические ошибки на сервер

2. **Производительность**:
   - Использовать пагинацию для больших списков
   - Оптимизировать размер изображений перед загрузкой
   - Использовать lazy loading для изображений

3. **UX**:
   - Показывать индикатор загрузки при запросах
   - Обрабатывать ошибки сети понятными сообщениями
   - Предоставлять возможность повторить запрос при ошибке

---

## 🧪 Тестирование

### Рекомендуемые тесты

1. **Unit тесты**:
   - Тесты Repository
   - Тесты ViewModel
   - Тесты валидации данных

2. **Integration тесты**:
   - Тесты API endpoints (с mock сервером)
   - Тесты аутентификации
   - Тесты синхронизации данных

3. **UI тесты**:
   - Тесты основных экранов
   - Тесты навигации
   - Тесты форм

---

## 📚 Полезные ссылки

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Retrofit Documentation](https://square.github.io/retrofit/)
- [OkHttp Documentation](https://square.github.io/okhttp/)

---

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Проверьте формат запроса
3. Убедитесь, что токен действителен
4. Проверьте права доступа для endpoint

---

**Версия документа**: 1.0  
**Дата обновления**: 2024-03-15
