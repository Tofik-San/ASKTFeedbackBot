from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or "<ТВОЙ_ТОКЕН>"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://asktfeedbackbot-production.up.railway.app{WEBHOOK_PATH}"

app = FastAPI()
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот ASKT работает через Webhook.")

application.add_handler(CommandHandler("start", start))

@app.on_event("startup")
async def on_startup():
    await application.bot.set_webhook(url=WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}
