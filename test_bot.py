# telegram_bot.py
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://152.114.192.9:2007"  # локальный Django сервер

# Состояния для ConversationHandler
REGISTER, LOGIN, SELECT_ROLE, COMPLETE_PROFILE = range(4)

user_data_store = {}  # временное хранение токена

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для тестирования SportRB API.\n"
        "Команды:\n"
        "/register - регистрация\n"
        "/login - вход\n"
        "/role - выбрать роль\n"
        "/profile - обновить профиль"
    )

# ----------- Регистрация -----------
async def register_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Регистрация. Отправь данные в формате:\n"
        "email, first_name, last_name, password"
    )
    return REGISTER

async def register_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email, first_name, last_name, password = update.message.text.split(",")
        payload = {
            "email": email.strip(),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "password": password.strip(),
            "password2": password.strip(),
        }
        r = requests.post(f"{API_URL}/api/auth/register/", json=payload)
        await update.message.reply_text(f"Регистрация: {r.status_code}\nОтвет: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    return ConversationHandler.END

# ----------- Логин -----------
async def login_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вход. Отправь данные в формате:\nemail, password"
    )
    return LOGIN

async def login_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email, password = update.message.text.split(",")
        payload = {"email": email.strip(), "password": password.strip()}
        r = requests.post(f"{API_URL}/api/auth/login/", json=payload)
        if r.status_code == 200:
            data = r.json()
            user_data_store[update.effective_user.id] = data['access']
            await update.message.reply_text(f"Вход успешен!\nAccess token сохранён.\n{data}")
        else:
            await update.message.reply_text(f"Ошибка входа: {r.status_code}\n{r.text}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    return ConversationHandler.END

# ----------- Выбор роли -----------
async def role_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбор роли. Отправь в формате:\nrole, city\nПример: athlete, Уфа"
    )
    return SELECT_ROLE

async def role_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        role, city = update.message.text.split(",")
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        payload = {"role": role.strip(), "city": city.strip()}
        r = requests.post(f"{API_URL}/api/users/select-role/", json=payload, headers=headers)
        await update.message.reply_text(f"Выбор роли: {r.status_code}\n{r.json()}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    return ConversationHandler.END

# ----------- Обновление профиля с consent -----------
async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Обновление профиля. Отправь в формате:\nemail, phone, city, consent (True/False)\n"
        "Пример: test2@example.com, +79001234567, Москва, True"
    )
    return COMPLETE_PROFILE

async def profile_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email, phone, city, consent = update.message.text.split(",")
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "email": email.strip(),
            "phone": phone.strip(),
            "city": city.strip(),
            "consent_given": consent.strip().lower() == "true"
        }
        r = requests.patch(f"{API_URL}/api/users/complete-profile/", json=payload, headers=headers)
        await update.message.reply_text(f"Обновление профиля: {r.status_code}\n{r.json()}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    return ConversationHandler.END

# ----------- Основной запуск -----------
if __name__ == "__main__":
    TOKEN = "8301988384:AAHn0Fa2HmG8hHpAP3H6-zSkXUXzLbHiRkk"  # вставь токен бота
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register_cmd),
                      CommandHandler('login', login_cmd),
                      CommandHandler('role', role_cmd),
                      CommandHandler('profile', profile_cmd)],
        states={
            REGISTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_step)],
            LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_step)],
            SELECT_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, role_step)],
            COMPLETE_PROFILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_step)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    print("Бот запущен!")
    app.run_polling()
