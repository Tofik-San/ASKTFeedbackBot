import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

# Ключевые слова для блокировки
BANNED_KEYWORDS = ["http", "https", "t.me", "бот", "порно", "viagra", "casino"]

async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.lower()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if any(keyword in message_text for keyword in BANNED_KEYWORDS):
        try:
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await update.message.reply_text("⛔ Нарушение. Пользователь забанен.")
        except Exception as e:
            logging.error(f"Ошибка при бане: {e}")
        return

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderate))
    app.run_polling()
