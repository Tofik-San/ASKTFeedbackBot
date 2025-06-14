from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Переменная должна строго совпадать с тем, что ты указал в Railway
TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
application = Application.builder().token(TOKEN).build()

# Пример команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает. Всё стабильно.")

application.add_handler(CommandHandler("start", start))

@app.post("/")
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()        # ← инициализация
    await application.start()             # ← запуск обработчика
    await application.process_update(update)
    await application.stop()              # ← корректная остановка
    return {"ok": True}
