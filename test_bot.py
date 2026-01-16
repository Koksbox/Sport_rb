# telegram_bot.py
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Замени на свой локальный адрес
API_URL = "http://152.114.192.9:2007"

# Состояния
(REGISTER, LOGIN, SELECT_ROLE, COMPLETE_PROFILE,
 CLUB_SEARCH, ENROLLMENT_REQUEST, EVENT_LIST,
 ACHIEVEMENTS, NOTIFICATIONS) = range(9)

user_data_store = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 SportRB Тест-бот\n\n"
        "Команды:\n"
        "/register - регистрация\n"
        "/login - вход\n"
        "/role - выбрать роль\n"
        "/profile - дополнить профиль\n"
        "/clubs - найти клубы\n"
        "/enroll - записаться в группу\n"
        "/events - мероприятия\n"
        "/achievements - достижения\n"
        "/notifications - уведомления"
    )


# --- Регистрация ---
async def register_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📧 Регистрация\nФормат: email, имя, фамилия, пароль")
    return REGISTER


async def register_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split(",")
        if len(parts) != 4:
            raise ValueError("Неверный формат")
        email, first_name, last_name, password = [p.strip() for p in parts]
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "password2": password
        }
        r = requests.post(f"{API_URL}/api/auth/register/", json=payload)
        if r.status_code == 201:
            await update.message.reply_text("✅ Регистрация успешна!")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Вход ---
async def login_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔑 Вход\nФормат: email, пароль")
    return LOGIN


async def login_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email, password = [p.strip() for p in update.message.text.split(",")]
        payload = {"email": email, "password": password}
        r = requests.post(f"{API_URL}/api/auth/login/", json=payload)
        if r.status_code == 200:
            token = r.json()['access']
            user_data_store[update.effective_user.id] = token
            await update.message.reply_text("✅ Вход успешен!")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Выбор роли ---
async def role_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 Выбор роли\nФормат: роль, город\n"
        "Роли: athlete, parent, organization\n"  # ← УДАЛИЛ 'coach'
        "Пример: athlete, Уфа"
    )
    return SELECT_ROLE


async def role_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        role, city = [p.strip() for p in update.message.text.split(",")]
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("❌ Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        payload = {"role": role, "city": city}
        r = requests.post(f"{API_URL}/api/users/select-role/", json=payload, headers=headers)
        if r.status_code == 201:
            await update.message.reply_text("✅ Роль выбрана!")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Дополнение профиля ---
async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Дополнить профиль\n"
        "Формат: email, телефон, город, согласие(True/False)\n"
        "Пример: test@test.com, +79001234567, Уфа, True"
    )
    return COMPLETE_PROFILE


async def profile_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email, phone, city, consent = [p.strip() for p in update.message.text.split(",")]
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("❌ Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "email": email,
            "phone": phone,
            "city": city,
            "consent_given": consent.lower() == "true"
        }
        r = requests.patch(f"{API_URL}/api/users/complete-profile/", json=payload, headers=headers)
        if r.status_code == 200:
            await update.message.reply_text("✅ Профиль обновлён!")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Поиск клубов ---
async def clubs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏟️ Поиск клубов\nВведите название или город")
    return CLUB_SEARCH


async def clubs_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.message.text.strip()
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("❌ Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{API_URL}/api/coaches/clubs/search/?name={query}", headers=headers)
        if r.status_code == 200:
            clubs = r.json()
            if clubs:
                msg = "🏆 Найденные клубы:\n"
                for club in clubs[:5]:
                    msg += f"\n{club['name']} ({club['city_name']})\nID: {club['id']}\n"
                await update.message.reply_text(msg)
            else:
                await update.message.reply_text("❌ Клубы не найдены")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Запись в группу ---
async def enroll_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Запись в группу\nВведите ID группы")
    return ENROLLMENT_REQUEST


async def enroll_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        group_id = int(update.message.text.strip())
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("❌ Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        payload = {"group": group_id}
        r = requests.post(f"{API_URL}/api/athletes/enrollment/request/", json=payload, headers=headers)
        if r.status_code == 201:
            await update.message.reply_text("✅ Заявка отправлена!")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Мероприятия ---
async def events_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Получение списка мероприятий...")
    return EVENT_LIST


async def events_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("❌ Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{API_URL}/api/events/", headers=headers)
        if r.status_code == 200:
            events = r.json()
            if events:
                msg = "🎉 Ближайшие мероприятия:\n"
                for event in events[:3]:
                    msg += f"\n{event['title']} ({event['start_date']})\nID: {event['id']}\n"
                await update.message.reply_text(msg)
            else:
                await update.message.reply_text("❌ Мероприятия не найдены")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Достижения ---
async def achievements_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏅 Получение достижений...")
    return ACHIEVEMENTS


async def achievements_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("❌ Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{API_URL}/api/achievements/achievements/", headers=headers)
        if r.status_code == 200:
            achievements = r.json()
            if achievements:
                msg = "🏆 Ваши достижения:\n"
                for ach in achievements[:5]:
                    msg += f"\n{ach['title']} ({ach['date']})\n"
                await update.message.reply_text(msg)
            else:
                await update.message.reply_text("❌ Достижений нет")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Уведомления ---
async def notifications_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔔 Получение уведомлений...")
    return NOTIFICATIONS


async def notifications_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        token = user_data_store.get(update.effective_user.id)
        if not token:
            await update.message.reply_text("❌ Сначала войдите (/login)")
            return ConversationHandler.END

        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{API_URL}/api/notifications/", headers=headers)
        if r.status_code == 200:
            notifications = r.json()
            if notifications:
                msg = "📩 Ваши уведомления:\n"
                for notif in notifications[:5]:
                    status = "✅" if notif['is_read'] else "🆕"
                    msg += f"\n{status} {notif['title']}\n{notif['body']}\n"
                await update.message.reply_text(msg)
            else:
                await update.message.reply_text("❌ Уведомлений нет")
        else:
            await update.message.reply_text(f"❌ Ошибка: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")
    return ConversationHandler.END


# --- Запуск ---
if __name__ == "__main__":
    TOKEN = "8301988384:AAHn0Fa2HmG8hHpAP3H6-zSkXUXzLbHiRkk"  # ← Замени на свой!
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('register', register_cmd),
            CommandHandler('login', login_cmd),
            CommandHandler('role', role_cmd),
            CommandHandler('profile', profile_cmd),
            CommandHandler('clubs', clubs_cmd),
            CommandHandler('enroll', enroll_cmd),
            CommandHandler('events', events_cmd),
            CommandHandler('achievements', achievements_cmd),
            CommandHandler('notifications', notifications_cmd),
        ],
        states={
            REGISTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_step)],
            LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_step)],
            SELECT_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, role_step)],
            COMPLETE_PROFILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_step)],
            CLUB_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, clubs_step)],
            ENROLLMENT_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, enroll_step)],
            EVENT_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, events_step)],
            ACHIEVEMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, achievements_step)],
            NOTIFICATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, notifications_step)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    print("✅ Бот запущен! Отправьте /start")
    app.run_polling()