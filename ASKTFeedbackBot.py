from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
application = Application.builder().token(TOKEN).build()

# Стартовая команда с кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👍 Понравилось", callback_data="like")],
        [InlineKeyboardButton("👎 Не понравилось", callback_data="dislike")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Оставь отзыв о канале:", reply_markup=reply_markup)

# Обработка нажатий
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "like":
        await query.message.reply_text("Отлично! Напиши, что именно понравилось.")
    elif query.data == "dislike":
        await query.message.reply_text("Спасибо! Напиши, что было не так.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

# Обработка Webhook
@app.post("/")
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return {"ok": True}
