# Примеры использования API для Android

## 🔧 Настройка Retrofit

### 1. Зависимости (build.gradle)

```kotlin
dependencies {
    // Retrofit
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"
    implementation "com.squareup.okhttp3:okhttp:4.11.0"
    implementation "com.squareup.okhttp3:logging-interceptor:4.11.0"
    
    // Coroutines
    implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"
    
    // Encrypted SharedPreferences
    implementation "androidx.security:security-crypto:1.1.0-alpha06"
}
```

### 2. Конфигурация Retrofit

```kotlin
object ApiClient {
    private const val BASE_URL = "https://yourdomain.ru/api/"
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor())
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        })
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val authApi: AuthApi = retrofit.create(AuthApi::class.java)
    val userApi: UserApi = retrofit.create(UserApi::class.java)
    val eventApi: EventApi = retrofit.create(EventApi::class.java)
    val organizationApi: OrganizationApi = retrofit.create(OrganizationApi::class.java)
}
```

### 3. Интерцептор для аутентификации

```kotlin
class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val tokenManager = TokenManager.getInstance()
        val accessToken = tokenManager.getAccessToken()
        
        val request = if (accessToken != null) {
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $accessToken")
                .addHeader("Content-Type", "application/json")
                .build()
        } else {
            chain.request()
        }
        
        var response = chain.proceed(request)
        
        // Если токен истек, пытаемся обновить
        if (response.code == 401 && accessToken != null) {
            val newToken = tokenManager.refreshTokenSync()
            if (newToken != null) {
                val newRequest = request.newBuilder()
                    .header("Authorization", "Bearer $newToken")
                    .build()
                response.close()
                response = chain.proceed(newRequest)
            }
        }
        
        return response
    }
}
```

---

## 📝 Data Models

### 1. Модели запросов

```kotlin
// Регистрация
data class RegisterRequest(
    val email: String,
    val password: String,
    val password2: String,
    val first_name: String,
    val last_name: String,
    val patronymic: String? = null,
    val phone: String? = null,
    val city: String? = null
)

// Вход
data class LoginRequest(
    val email: String,
    val password: String
)

// Выбор роли (спортсмен)
data class SelectRoleAthleteRequest(
    val role: String = "athlete",
    val city: String,
    val sport_id: Int,
    val birth_date: String? = null
)

// Выбор роли (тренер)
data class SelectRoleCoachRequest(
    val role: String = "coach",
    val city_coach: String,
    val specialization_id: Int,
    val experience_years: Int
)

// Регистрация на мероприятие
data class RegisterEventRequest(
    val athlete_id: Int? = null,
    val group_id: Int? = null
)
```

### 2. Модели ответов

```kotlin
// Ответ входа
data class LoginResponse(
    val access: String,
    val refresh: String,
    val user: User? = null,
    val needs_role_selection: Boolean = false,
    val active_role: String? = null
)

// Ответ регистрации
data class RegisterResponse(
    val message: String,
    val user_id: Int,
    val email: String,
    val needs_role_selection: Boolean
)

// Пользователь
data class User(
    val id: Int,
    val email: String,
    val first_name: String,
    val last_name: String,
    val patronymic: String? = null,
    val birth_date: String? = null,
    val phone: String? = null,
    val city: String? = null,
    val photo_url: String? = null
)

// Роль
data class Role(
    val role: String,
    val role_name: String,
    val unique_id: String,
    val created_at: String,
    val is_active: Boolean
)

// Мероприятие
data class Event(
    val id: Int,
    val name: String,
    val description: String? = null,
    val start_date: String,
    val end_date: String? = null,
    val location: String? = null,
    val city: String? = null,
    val sport: String? = null,
    val age_groups: List<AgeGroup>? = null,
    val registration_open: Boolean = false,
    val is_registered: Boolean = false,
    val participants_count: Int = 0,
    val max_participants: Int? = null
)

data class AgeGroup(
    val min_age: Int,
    val max_age: Int
)

// Организация
data class Organization(
    val id: Int,
    val name: String,
    val org_type: String,
    val city: String,
    val address: String? = null,
    val latitude: String? = null,
    val longitude: String? = null,
    val website: String? = null,
    val sports: List<String>? = null
)

// Профиль спортсмена
data class AthleteProfile(
    val id: Int,
    val user: User,
    val city: City,
    val main_sport: Sport,
    val school_or_university: String? = null,
    val health_group: String? = null,
    val goals: List<String>? = null
)

data class City(
    val id: Int,
    val name: String,
    val region: String
)

data class Sport(
    val id: Int,
    val name: String,
    val category: String? = null
)
```

---

## 🔐 API Interfaces

### 1. AuthApi

```kotlin
interface AuthApi {
    @POST("auth/register/")
    suspend fun register(@Body request: RegisterRequest): Response<RegisterResponse>
    
    @POST("auth/login/")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
    
    @POST("auth/token/refresh/")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<RefreshTokenResponse>
    
    @POST("auth/telegram/")
    suspend fun loginTelegram(@Body request: TelegramLoginRequest): Response<LoginResponse>
    
    @POST("auth/vk/")
    suspend fun loginVK(@Body request: VKLoginRequest): Response<LoginResponse>
}

data class RefreshTokenRequest(val refresh: String)
data class RefreshTokenResponse(val access: String)
data class TelegramLoginRequest(val init_data: String)
data class VKLoginRequest(val access_token: String)
```

### 2. UserApi

```kotlin
interface UserApi {
    @GET("users/roles/")
    suspend fun getRoles(): Response<RolesResponse>
    
    @POST("users/select-role/")
    suspend fun selectRole(@Body request: SelectRoleRequest): Response<SelectRoleResponse>
    
    @POST("users/switch-role/")
    suspend fun switchRole(@Body request: SwitchRoleRequest): Response<SwitchRoleResponse>
    
    @GET("users/role-id/")
    suspend fun getRoleId(): Response<RoleIdResponse>
    
    @GET("users/basic-data/")
    suspend fun getBasicData(): Response<User>
}

data class RolesResponse(val roles: List<Role>)
data class SelectRoleResponse(
    val message: String,
    val role: String,
    val needs_profile_completion: Boolean,
    val profile_url: String? = null,
    val redirect_to: String
)
data class SwitchRoleRequest(val role: String)
data class SwitchRoleResponse(val success: Boolean, val role: String)
data class RoleIdResponse(
    val role: String,
    val unique_id: String,
    val role_name: String
)
```

### 3. EventApi

```kotlin
interface EventApi {
    @GET("events/")
    suspend fun getEvents(
        @Query("status") status: String? = null,
        @Query("sport") sport: String? = null,
        @Query("city") city: String? = null
    ): Response<List<Event>>
    
    @GET("events/{event_id}/")
    suspend fun getEvent(@Path("event_id") eventId: Int): Response<Event>
    
    @POST("events/{event_id}/register/")
    suspend fun registerForEvent(@Path("event_id") eventId: Int): Response<RegisterEventResponse>
    
    @POST("events/{event_id}/cancel/")
    suspend fun cancelRegistration(@Path("event_id") eventId: Int): Response<CancelRegistrationResponse>
    
    @GET("events/my/")
    suspend fun getMyEvents(): Response<List<Event>>
}

data class RegisterEventResponse(
    val message: String,
    val registration_id: Int
)
data class CancelRegistrationResponse(val message: String)
```

### 4. OrganizationApi

```kotlin
interface OrganizationApi {
    @GET("organizations/")
    suspend fun getOrganizations(
        @Query("city") city: String? = null,
        @Query("sport") sport: String? = null
    ): Response<List<Organization>>
    
    @GET("organizations/{org_id}/")
    suspend fun getOrganization(@Path("org_id") orgId: Int): Response<Organization>
    
    @Multipart
    @POST("organizations/create/")
    suspend fun createOrganization(
        @Part("name") name: RequestBody,
        @Part("org_type") orgType: RequestBody,
        @Part("city_id") cityId: RequestBody,
        @Part("address") address: RequestBody,
        @Part("latitude") latitude: RequestBody,
        @Part("longitude") longitude: RequestBody,
        @Part("inn") inn: RequestBody,
        @Part documents: List<MultipartBody.Part>? = null
    ): Response<CreateOrganizationResponse>
}

data class CreateOrganizationResponse(
    val id: Int,
    val name: String,
    val status: String,
    val message: String
)
```

### 5. AthleteApi

```kotlin
interface AthleteApi {
    @GET("athletes/profile/")
    suspend fun getProfile(): Response<AthleteProfile>
    
    @PUT("athletes/profile/")
    suspend fun updateProfile(@Body request: UpdateProfileRequest): Response<AthleteProfile>
    
    @GET("athletes/progress/")
    suspend fun getProgress(): Response<ProgressResponse>
}

data class UpdateProfileRequest(
    val school_or_university: String? = null,
    val health_group: String? = null,
    val goals: List<String>? = null,
    val medical_restrictions: List<String>? = null,
    val allergies: String? = null,
    val emergency_contact_name: String? = null,
    val emergency_contact_phone: String? = null
)

data class ProgressResponse(
    val attendance: Map<String, Int>,
    val events: List<EventProgress>,
    val achievements: List<Achievement>
)

data class EventProgress(
    val id: Int,
    val name: String,
    val date: String,
    val result: String? = null
)

data class Achievement(
    val id: Int,
    val title: String,
    val date: String,
    val description: String? = null
)
```

---

## 🏗️ Repository Pattern

### 1. AuthRepository

```kotlin
class AuthRepository(
    private val api: AuthApi,
    private val tokenManager: TokenManager
) {
    suspend fun register(request: RegisterRequest): Result<RegisterResponse> {
        return try {
            val response = api.register(request)
            if (response.isSuccessful) {
                response.body()?.let { Result.success(it) }
                    ?: Result.failure(Exception("Empty response"))
            } else {
                val error = parseError(response.errorBody())
                Result.failure(Exception(error))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun login(email: String, password: String): Result<LoginResponse> {
        return try {
            val response = api.login(LoginRequest(email, password))
            if (response.isSuccessful) {
                response.body()?.let {
                    tokenManager.saveTokens(it.access, it.refresh)
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                val error = parseError(response.errorBody())
                Result.failure(Exception(error))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun refreshToken(): Result<String> {
        return try {
            val refreshToken = tokenManager.getRefreshToken()
            if (refreshToken == null) {
                return Result.failure(Exception("No refresh token"))
            }
            
            val response = api.refreshToken(RefreshTokenRequest(refreshToken))
            if (response.isSuccessful) {
                response.body()?.let {
                    tokenManager.saveAccessToken(it.access)
                    Result.success(it.access)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                Result.failure(Exception("Token refresh failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun parseError(errorBody: ResponseBody?): String {
        return try {
            val errorJson = JSONObject(errorBody?.string() ?: "{}")
            errorJson.optString("error") ?: "Unknown error"
        } catch (e: Exception) {
            "Unknown error"
        }
    }
}
```

### 2. EventRepository

```kotlin
class EventRepository(
    private val api: EventApi,
    private val localDb: AppDatabase
) {
    suspend fun getEvents(
        status: String? = null,
        sport: String? = null,
        city: String? = null
    ): Result<List<Event>> {
        return try {
            val response = api.getEvents(status, sport, city)
            if (response.isSuccessful) {
                response.body()?.let { events ->
                    // Кэшируем в локальную БД
                    localDb.eventDao().insertAll(events)
                    Result.success(events)
                } ?: Result.failure(Exception("Empty response"))
            } else {
                // Пытаемся получить из кэша
                val cachedEvents = localDb.eventDao().getAll()
                if (cachedEvents.isNotEmpty()) {
                    Result.success(cachedEvents)
                } else {
                    Result.failure(Exception("Failed to fetch events"))
                }
            }
        } catch (e: Exception) {
            // Пытаемся получить из кэша
            val cachedEvents = localDb.eventDao().getAll()
            if (cachedEvents.isNotEmpty()) {
                Result.success(cachedEvents)
            } else {
                Result.failure(e)
            }
        }
    }
    
    suspend fun registerForEvent(eventId: Int): Result<RegisterEventResponse> {
        return try {
            val response = api.registerForEvent(eventId)
            if (response.isSuccessful) {
                response.body()?.let { Result.success(it) }
                    ?: Result.failure(Exception("Empty response"))
            } else {
                val error = parseError(response.errorBody())
                Result.failure(Exception(error))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

## 🎯 ViewModel Examples

### 1. AuthViewModel

```kotlin
class AuthViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _loginState = MutableStateFlow<ApiResult<LoginResponse>>(ApiResult.Loading)
    val loginState: StateFlow<ApiResult<LoginResponse>> = _loginState
    
    private val _registerState = MutableStateFlow<ApiResult<RegisterResponse>>(ApiResult.Loading)
    val registerState: StateFlow<ApiResult<RegisterResponse>> = _registerState
    
    fun login(email: String, password: String) {
        viewModelScope.launch {
            _loginState.value = ApiResult.Loading
            authRepository.login(email, password)
                .onSuccess { _loginState.value = ApiResult.Success(it) }
                .onFailure { _loginState.value = ApiResult.Error(it.message ?: "Unknown error", 0) }
        }
    }
    
    fun register(request: RegisterRequest) {
        viewModelScope.launch {
            _registerState.value = ApiResult.Loading
            authRepository.register(request)
                .onSuccess { _registerState.value = ApiResult.Success(it) }
                .onFailure { _registerState.value = ApiResult.Error(it.message ?: "Unknown error", 0) }
        }
    }
}
```

### 2. EventViewModel

```kotlin
class EventViewModel(
    private val eventRepository: EventRepository
) : ViewModel() {
    
    private val _events = MutableStateFlow<List<Event>>(emptyList())
    val events: StateFlow<List<Event>> = _events
    
    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error
    
    fun loadEvents(status: String? = null, sport: String? = null, city: String? = null) {
        viewModelScope.launch {
            _loading.value = true
            _error.value = null
            
            eventRepository.getEvents(status, sport, city)
                .onSuccess { _events.value = it }
                .onFailure { _error.value = it.message }
            
            _loading.value = false
        }
    }
    
    fun registerForEvent(eventId: Int) {
        viewModelScope.launch {
            eventRepository.registerForEvent(eventId)
                .onSuccess { 
                    // Обновляем список событий
                    loadEvents()
                }
                .onFailure { _error.value = it.message }
        }
    }
}
```

---

## 💾 Token Manager

```kotlin
class TokenManager(context: Context) {
    private val encryptedPrefs = EncryptedSharedPreferences.create(
        "token_prefs",
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        context,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    private val accessTokenKey = "access_token"
    private val refreshTokenKey = "refresh_token"
    
    fun saveTokens(access: String, refresh: String) {
        encryptedPrefs.edit()
            .putString(accessTokenKey, access)
            .putString(refreshTokenKey, refresh)
            .apply()
    }
    
    fun getAccessToken(): String? {
        return encryptedPrefs.getString(accessTokenKey, null)
    }
    
    fun getRefreshToken(): String? {
        return encryptedPrefs.getString(refreshTokenKey, null)
    }
    
    fun saveAccessToken(access: String) {
        encryptedPrefs.edit()
            .putString(accessTokenKey, access)
            .apply()
    }
    
    fun clearTokens() {
        encryptedPrefs.edit()
            .remove(accessTokenKey)
            .remove(refreshTokenKey)
            .apply()
    }
    
    suspend fun refreshTokenSync(): String? {
        val refreshToken = getRefreshToken() ?: return null
        
        return try {
            val response = ApiClient.authApi.refreshToken(RefreshTokenRequest(refreshToken))
            if (response.isSuccessful) {
                response.body()?.access?.also { saveAccessToken(it) }
            } else {
                null
            }
        } catch (e: Exception) {
            null
        }
    }
    
    companion object {
        @Volatile
        private var INSTANCE: TokenManager? = null
        
        fun getInstance(context: Context): TokenManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: TokenManager(context.applicationContext).also { INSTANCE = it }
            }
        }
    }
}
```

---

## 🔄 Error Handling

```kotlin
sealed class ApiResult<out T> {
    data class Success<out T>(val data: T) : ApiResult<T>()
    data class Error(val message: String, val code: Int) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}

fun <T> handleApiResponse(response: Response<T>): ApiResult<T> {
    return when {
        response.isSuccessful -> {
            response.body()?.let { ApiResult.Success(it) }
                ?: ApiResult.Error("Empty response", response.code())
        }
        response.code() == 401 -> {
            ApiResult.Error("Unauthorized", 401)
        }
        response.code() == 403 -> {
            ApiResult.Error("Forbidden", 403)
        }
        response.code() == 404 -> {
            ApiResult.Error("Not found", 404)
        }
        else -> {
            val errorBody = response.errorBody()?.string()
            val errorMessage = try {
                JSONObject(errorBody ?: "{}").optString("error") ?: "Unknown error"
            } catch (e: Exception) {
                "Unknown error"
            }
            ApiResult.Error(errorMessage, response.code())
        }
    }
}
```

---

## 📱 Usage Example

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var viewModel: EventViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val repository = EventRepository(ApiClient.eventApi, AppDatabase.getDatabase(this))
        viewModel = ViewModelProvider(this, EventViewModelFactory(repository))[EventViewModel::class.java]
        
        // Наблюдаем за событиями
        lifecycleScope.launch {
            viewModel.events.collect { events ->
                // Обновляем UI
                updateEventsList(events)
            }
        }
        
        // Наблюдаем за ошибками
        lifecycleScope.launch {
            viewModel.error.collect { error ->
                error?.let {
                    showError(it)
                }
            }
        }
        
        // Загружаем события
        viewModel.loadEvents()
    }
}
```

---

**Версия документа**: 1.0  
**Дата обновления**: 2024-03-15
