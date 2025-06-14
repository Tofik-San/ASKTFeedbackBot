import os
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler, ContextTypes, ChatMemberHandler
)

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_CHAT_ID = -1002794841645

app = FastAPI()
application = Application.builder().token(TOKEN).build()

# Приветствие при входе
async def greet_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member
    if member.new_chat_member.status == "member":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 Понравилось", callback_data="like")],
            [InlineKeyboardButton("👎 Не понравилось", callback_data="dislike")]
        ])
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"Привет, {member.from_user.first_name}!\nОставь отзыв о боте:",
            reply_markup=keyboard
        )

# Обработка нажатий на кнопки
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "like":
        await query.message.reply_text("Спасибо! А теперь напиши, что именно понравилось.")
    elif query.data == "dislike":
        await query.message.reply_text("Жаль. Расскажи, что не устроило.")

# Модерация: удаление спама / мата / ссылок
BAD_WORDS = ["хуй", "пизд", "еба", "нахуй", "сука", "порно", "http", "t.me", "https"]

async def moderate_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.message.from_user.id

    if any(bad in text for bad in BAD_WORDS):
        await update.message.delete()
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"Сообщение удалено. Пользователь нарушил правила."
        )
        try:
            await context.bot.ban_chat_member(GROUP_CHAT_ID, user_id)
        except:
            pass  # бот должен иметь права администратора

# Старт-команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает в группе для отзывов.")

# Роут вебхука
@app.post("/")
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return {"ok": True}

# Регистрация хендлеров
application.add_handler(ChatMemberHandler(greet_user, ChatMemberHandler.CHAT_MEMBER))
application.add_handler(CallbackQueryHandler(handle_feedback))
application.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_CHAT_ID), moderate_messages))
application.add_handler(CommandHandler("start", start))
