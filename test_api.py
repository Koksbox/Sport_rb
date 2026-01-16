import requests

BASE_URL = "http://127.0.0.1:8000"

def safe_print_response(r, step):
    print(f"\n=== {step} ===")
    print("Status code:", r.status_code)
    try:
        print("JSON response:", r.json())
    except Exception:
        print("Text response:", r.text)

# -----------------------------
# 1️⃣ Регистрация пользователя
# -----------------------------
register_data = {
    "email": "test@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "password": "securepassword123",
    "password2": "securepassword123"
}

r = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
safe_print_response(r, "Регистрация")

# -----------------------------
# 2️⃣ Логин и получение JWT
# -----------------------------
login_data = {
    "email": "test@example.com",
    "password": "securepassword123"
}

r = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
safe_print_response(r, "Логин")

access_token = r.json().get("access") if r.headers.get("Content-Type") == "application/json" else None
if not access_token:
    print("❌ Токен не получен. Проверь, что сервер запущен и API доступен.")
    exit()

headers = {"Authorization": f"Bearer {access_token}"}

# -----------------------------
# 3️⃣ Выбор роли (athlete)
# -----------------------------
role_data = {
    "role": "athlete",
    "city": "Уфа"
}

r = requests.post(f"{BASE_URL}/api/users/select-role/", headers=headers, json=role_data)
safe_print_response(r, "Выбор роли")
