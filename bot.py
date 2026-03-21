import logging
import os
import json
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "8653082594:AAGvap2Z7L_v308Wej6Jk3yWYaQDdei9_F0")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "highsecurityprison20110403")
DATA_FILE = "data.json"

# ---------- helpers ----------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admins": [], "users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_admins():
    return load_data()["admins"]

def is_admin(user_id: int) -> bool:
    return user_id in get_admins()

def register_user(user_id: int, username: str, full_name: str):
    data = load_data()
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {"username": username, "full_name": full_name, "messages": 0}
    save_data(data)

def increment_msg(user_id: int):
    data = load_data()
    uid = str(user_id)
    if uid in data["users"]:
        data["users"][uid]["messages"] += 1
        save_data(data)

# ---------- keyboards ----------

def main_menu():
    keyboard = [
        [KeyboardButton("📩 Написать админу"), KeyboardButton("📋 FAQ")],
        [KeyboardButton("🌐 Контакты"), KeyboardButton("⭐ Оставить отзыв")],
        [KeyboardButton("ℹ️ О боте")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_menu():
    keyboard = [
        [KeyboardButton("👥 Все пользователи"), KeyboardButton("📢 Рассылка")],
        [KeyboardButton("📩 Написать админу"), KeyboardButton("📋 FAQ")],
        [KeyboardButton("🌐 Контакты"), KeyboardButton("⭐ Оставить отзыв")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------- /start ----------

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or "", user.full_name)
    menu = admin_menu() if is_admin(user.id) else main_menu()
    await update.message.reply_text(
        f"👋 Привет, *{user.first_name}*\\!\n\n"
        "Я помогу тебе связаться с администратором, найти ответы на вопросы "
        "и узнать полезную информацию\\. Выбери действие ниже:",
        parse_mode="MarkdownV2",
        reply_markup=menu,
    )

# ---------- /admin ----------

async def admin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not ctx.args:
        await update.message.reply_text("🔑 Используй: /admin <пароль>")
        return
    password = " ".join(ctx.args)
    if password == ADMIN_PASSWORD:
        data = load_data()
        if user.id not in data["admins"]:
            data["admins"].append(user.id)
            save_data(data)
            logger.info("New admin: %s (%d)", user.full_name, user.id)
            await update.message.reply_text(
                "✅ Ты теперь *администратор\\!*\n\n"
                "Все сообщения пользователей будут приходить тебе\\.\n"
                "Чтобы ответить — просто сделай *Reply* на сообщение\\.",
                parse_mode="MarkdownV2",
                reply_markup=admin_menu(),
            )
        else:
            await update.message.reply_text("ℹ️ Ты уже администратор.")
    else:
        await update.message.reply_text("❌ Неверный пароль.")

# ---------- /revoke ----------

async def revoke_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Ты не являешься администратором.")
        return
    data = load_data()
    data["admins"].remove(user.id)
    save_data(data)
    await update.message.reply_text(
        "✅ Права администратора сняты.", reply_markup=main_menu()
    )

# ---------- contacts ----------

async def contacts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✈️ Telegram канал", url="https://t.me/macanxyecocina")],
    ])
    await update.message.reply_text(
        "🌐 *Контакты и соцсети*\n\nВыбери нужную платформу:",
        parse_mode="Markdown",
        reply_markup=kb,
    )

# ---------- faq ----------

FAQ = [
    ("❓ Как с вами связаться?", "Нажми «📩 Написать админу» и напиши свой вопрос — мы ответим в ближайшее время."),
    ("❓ Как оставить отзыв?", "Нажми «⭐ Оставить отзыв» в меню."),
    ("❓ Где вы находитесь?", "Мы работаем онлайн и принимаем клиентов со всего мира."),
    ("❓ Как отписаться от рассылки?", "Напиши админу «отписаться» — мы исключим тебя из рассылок."),
]

async def faq(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = "📋 *Частые вопросы:*\n\n"
    for q, a in FAQ:
        text += f"{q}\n_{a}_\n\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# ---------- about ----------

async def about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *О боте*\n\n"
        "Этот бот создан для удобной связи с администратором\\.\n\n"
        "🔧 *Возможности:*\n"
        "• Прямая связь с командой\n"
        "• Быстрые ответы на частые вопросы\n"
        "• Ссылки на соцсети\n"
        "• Форма обратной связи\n"
        "• Рассылки от администратора\n\n"
        "📌 Версия: 1\\.0\\.0",
        parse_mode="MarkdownV2",
    )

# ---------- feedback ----------

async def feedback_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["waiting_feedback"] = True
    await update.message.reply_text(
        "⭐ *Оставь отзыв*\n\nНапиши свой отзыв в следующем сообщении — "
        "он будет передан администратору.",
        parse_mode="Markdown",
    )

# ---------- ask admin ----------

async def ask_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["waiting_question"] = True
    await update.message.reply_text(
        "📩 *Написать админу*\n\nНапиши своё сообщение — я передам его администратору.",
        parse_mode="Markdown",
    )

# ---------- users list (admin only) ----------

async def users_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    data = load_data()
    users = data.get("users", {})
    if not users:
        await update.message.reply_text("👥 Пользователей пока нет.")
        return
    text = f"👥 *Все пользователи* ({len(users)}):\n\n"
    for uid, info in list(users.items())[-20:]:  # last 20
        name = info.get("full_name", "—")
        uname = f"@{info['username']}" if info.get("username") else "без username"
        msgs = info.get("messages", 0)
        text += f"• {name} ({uname}) — {msgs} сообщ.\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# ---------- broadcast ----------

async def broadcast_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    ctx.user_data["waiting_broadcast"] = True
    await update.message.reply_text(
        "📢 *Рассылка*\n\nНапиши текст сообщения для рассылки всем пользователям.",
        parse_mode="Markdown",
    )

# ---------- main message handler ----------

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or ""
    register_user(user.id, user.username or "", user.full_name)
    increment_msg(user.id)

    # ---- button routing ----
    if text == "🌐 Контакты":
        await contacts(update, ctx); return
    if text == "📋 FAQ":
        await faq(update, ctx); return
    if text == "ℹ️ О боте":
        await about(update, ctx); return
    if text == "⭐ Оставить отзыв":
        await feedback_prompt(update, ctx); return
    if text == "📩 Написать админу":
        await ask_prompt(update, ctx); return
    if text == "👥 Все пользователи":
        await users_list(update, ctx); return
    if text == "📢 Рассылка":
        await broadcast_prompt(update, ctx); return

    # ---- admin replying to a user ----
    if is_admin(user.id) and update.message.reply_to_message:
        original = update.message.reply_to_message.text or ""
        # extract user_id from forwarded header
        if "ID:" in original:
            try:
                target_id = int(original.split("ID:")[1].split(")")[0].strip())
                await ctx.bot.send_message(
                    chat_id=target_id,
                    text=f"💬 *Ответ администратора:*\n\n{text}",
                    parse_mode="Markdown",
                )
                await update.message.reply_text("✅ Ответ отправлен пользователю.")
                return
            except Exception as e:
                logger.error("Reply error: %s", e)

    # ---- broadcast ----
    if ctx.user_data.get("waiting_broadcast") and is_admin(user.id):
        ctx.user_data["waiting_broadcast"] = False
        data = load_data()
        sent = 0
        for uid in data["users"]:
            try:
                await ctx.bot.send_message(
                    chat_id=int(uid),
                    text=f"📢 *Сообщение от администратора:*\n\n{text}",
                    parse_mode="Markdown",
                )
                sent += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Рассылка отправлена {sent} пользователям.")
        return

    # ---- feedback ----
    if ctx.user_data.get("waiting_feedback"):
        ctx.user_data["waiting_feedback"] = False
        uname = f"@{user.username}" if user.username else user.full_name
        await forward_to_admins(
            ctx,
            f"⭐ *Отзыв от* {uname} (ID: {user.id})\n\n{text}",
            user.id,
        )
        await update.message.reply_text("✅ Спасибо за отзыв! Мы обязательно его прочитаем. 🙏")
        return

    # ---- ask question ----
    if ctx.user_data.get("waiting_question"):
        ctx.user_data["waiting_question"] = False
        uname = f"@{user.username}" if user.username else user.full_name
        await forward_to_admins(
            ctx,
            f"📩 *Вопрос от* {uname} (ID: {user.id})\n\n{text}",
            user.id,
        )
        await update.message.reply_text("✅ Сообщение отправлено администратору! Ждите ответа. ⏳")
        return

    # ---- any other message → forward to admins ----
    if not is_admin(user.id):
        uname = f"@{user.username}" if user.username else user.full_name
        await forward_to_admins(
            ctx,
            f"💬 *Сообщение от* {uname} (ID: {user.id})\n\n{text}",
            user.id,
        )
        await update.message.reply_text(
            "📨 Твоё сообщение получено! Администратор ответит тебе в ближайшее время.",
            reply_markup=main_menu(),
        )

async def forward_to_admins(ctx: ContextTypes.DEFAULT_TYPE, text: str, sender_id: int):
    admins = get_admins()
    if not admins:
        return
    for admin_id in admins:
        if admin_id != sender_id:
            try:
                await ctx.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error("Forward to admin %d failed: %s", admin_id, e)

# ---------- main ----------

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("revoke", revoke_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
