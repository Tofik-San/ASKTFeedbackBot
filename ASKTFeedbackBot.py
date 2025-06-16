import os
from fastapi import FastAPI, Request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()
telegram_app = Application.builder().token(BOT_TOKEN).build()
client = OpenAI(api_key=OPENAI_API_KEY)

# Хранилище состояний пользователей
user_mode = {}
completed_users = set()

# Кнопки выбора направления
mode_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("Бизнес")], [KeyboardButton("Учёба")],
              [KeyboardButton("Маркетинг")], [KeyboardButton("Работа")]],
    resize_keyboard=True, one_time_keyboard=True
)

# Системный промт
system_prompt_base = """Ты — админ-бот, который принимает и обрабатывает отзывы пользователей после работы с одним из четырёх GPT-ботов: «Бизнес», «Учёба», «Маркетинг», «Работа».

🎯 Твоя задача:
— Принять отзыв.
— Классифицировать его по эмоциональному тону и содержанию.
— Выдать одну короткую реакцию, соответствующую стилю отзыва.

📌 Единственный вопрос, который ты имеешь право задать:
Если не указан бот, с которым работал пользователь (`mode`), сначала спроси:
"С каким ботом работал(а): бизнес, учёба, маркетинг или работа?"  
Дождись ответа. Затем — среагируй. Больше ничего не спрашиваешь.

🧷 Итог:
Каждый ответ — как реакция живого, нормального человека. Метко. Коротко. Без церемоний. Только реакция. Без продолжений.
"""

# GPT обработка текста
async def process_text_with_gpt(user_text: str, mode: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt_base},
            {"role": "user", "content": f"Mode: {mode}\nОтзыв: {user_text}"}
        ]
    )
    return response.choices[0].message.content.strip()

# Обработка выбора направления
@telegram_app.message_handler(filters.TEXT & filters.Regex("^(Бизнес|Учёба|Маркетинг|Работа)$"))
async def handle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in completed_users:
        return
    user_mode[user_id] = update.message.text
    await update.message.reply_text("Теперь напишите ваш отзыв.", reply_markup=None)

# Обработка отзыва
@telegram_app.message_handler(filters.TEXT)
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    if user_id in completed_users:
        return

    if user_id not in user_mode:
        await update.message.reply_text(
            "С каким ботом работал(а): бизнес, учёба, маркетинг или работа?",
            reply_markup=mode_keyboard
        )
        return

    mode = user_mode.get(user_id)
    gpt_reply = await process_text_with_gpt(user_text, mode)
    await update.message.reply_text(gpt_reply)

    completed_users.add(user_id)
    user_mode.pop(user_id, None)

# Webhook обработка
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    await telegram_app.update_queue.put(Update.de_json(data, telegram_app.bot))
    return {"ok": True}
