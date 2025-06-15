import os
import openai
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, ContextTypes, filters
)

# Получаем ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Устанавливаем ключ OpenAI
openai.api_key = OPENAI_API_KEY

# Инициализация FastAPI и Telegram App
app = FastAPI()
application = Application.builder().token(BOT_TOKEN).build()

# Обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_message = update.message.text

        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты дружелюбный и краткий бот для сбора отзывов. Отвечай по делу, с лёгким юмором, без воды."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=100,
                temperature=0.7
            )
            reply = gpt_response.choices[0].message.content.strip()
            await update.message.reply_text(reply)

        except Exception as e:
            print(f"OpenAI error: {e}")
            await update.message.reply_text("Ошибка при обработке. Попробуй снова позже.")

# Добавляем обработчик всех текстов
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook endpoint
@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return {"ok": True}
