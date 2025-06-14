import os
from fastapi import FastAPI, Request
from telegram import Update, ChatMemberUpdated
from telegram.ext import Application, ChatMemberHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "0"))

app = FastAPI()
application = Application.builder().token(TOKEN).build()


async def greet_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member: ChatMemberUpdated = update.chat_member
    if member.new_chat_member.status == "member":
        chat_id = member.chat.id
        if chat_id == GROUP_CHAT_ID:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Привет! Не держи в себе — выскажись по делу. Именно для этого я здесь."
            )

application.add_handler(ChatMemberHandler(greet_new_user, ChatMemberHandler.CHAT_MEMBER))

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return {"ok": True}
