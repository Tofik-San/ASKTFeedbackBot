import os
from fastapi import FastAPI, Request
from telegram import (
    Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
)
from telegram.ext import (
    Application, ContextTypes, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler
)

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@ASKT_Feedback"

app = FastAPI()
bot_app = Application.builder().token(TOKEN).build()


# 👉 Стартовое приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👍 Понравилось", callback_data="like")],
        [InlineKeyboardButton("👎 Не понравилось", callback_data="dislike")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Оставь отзыв о канале:", reply_markup=reply_markup)


# 👉 Обработка нажатия кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "like":
        await query.edit_message_text("Отлично! Напиши, что именно понравилось.")
    elif query.data == "dislike":
        await query.edit_message_text("Спасибо! Напиши, что было не так.")


# 👉 Проверка сообщений на флуд/запрещёнку
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.message.from_user.id

    bad_words = ["хуй", "пизда", "еблан", "сука"]
    if any(word in text for word in bad_words) or len(text) > 300:
        await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=user_id)
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="Пользователь заблокирован за нарушение.")
        return

    await context.bot.send_message(chat_id=CHANNEL_ID,
                                   text=f"✍ Отзыв от @{update.message.from_user.username or 'пользователя'}:\n\n{text}")


# 👉 Webhook-обработка
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    print(data)  # временно для логов Railway

    update = Update.de_json(data, bot_app.bot)
    await bot_app.initialize()
    await bot_app.process_update(update)
    return {"ok": True}


# 👉 Роутинг
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(button_handler))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
