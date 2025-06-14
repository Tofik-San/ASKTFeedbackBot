import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telebot import TeleBot, types

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = TeleBot(TOKEN)
app = FastAPI()

BAD_WORDS = {"хуй", "пизда", "ебать", "нахуй", "гандон"}
SPAM_PATTERNS = ["http", "t.me", "@"]

@app.post("/")
async def webhook(req: Request):
    try:
        data = await req.json()
        msg = types.Update.de_json(data).message
        if msg:
            uid = msg.from_user.id
            cid = msg.chat.id
            txt = msg.text.lower() if msg.text else ""

            if any(w in txt for w in BAD_WORDS | set(SPAM_PATTERNS)):
                bot.ban_chat_member(cid, uid)
                bot.send_message(cid, f"🚫 {msg.from_user.first_name} забанен.")
    except Exception as e:
        print("💥", e)
    return JSONResponse(content={"ok": True})
