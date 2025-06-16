from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
MAIN_BOT_LINK = 'https://t.me/ASKTbot'  # ссылка на основного бота

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Память для выбранного направления и флага завершённого диалога
user_mode = {}
completed_users = set()

# Кнопки для выбора направления
mode_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
mode_keyboard.add(
    KeyboardButton("Бизнес"),
    KeyboardButton("Учёба"),
    KeyboardButton("Маркетинг"),
    KeyboardButton("Работа")
)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id in completed_users:
        await message.answer("Спасибо, отзыв уже получен. Если хотите вернуться — вот бот: " + MAIN_BOT_LINK)
    else:
        await message.answer("Выберите направление, с которым вы работали:", reply_markup=mode_keyboard)

@dp.message_handler(lambda message: message.text in ["Бизнес", "Учёба", "Маркетинг", "Работа"])
async def select_mode(message: types.Message):
    user_id = message.from_user.id
    if user_id in completed_users:
        return
    user_mode[user_id] = message.text
    await message.answer("Ок. Теперь пришлите отзыв.", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler()
async def handle_feedback(message: types.Message):
    user_id = message.from_user.id
    if user_id in completed_users:
        await message.answer("Отзыв уже принят. Вернуться можно по ссылке: " + MAIN_BOT_LINK)
        return

    mode = user_mode.get(user_id)
    if not mode:
        await message.answer("Сначала выберите направление: /start")
        return

    feedback = message.text.strip().lower()

    if any(x in feedback for x in ["спасибо", "топ", "огонь", "кайф"]):
        response = "Рад, что зашло."
    elif any(x in feedback for x in ["такое", "сойдёт", "на троечку"]):
        response = "Ну хоть не проклял — уже прогресс :)"
    elif any(x in feedback for x in ["говно", "не работает", "удаляю"]):
        response = "Бывает. Сегодня не его день."
    elif any(x in feedback for x in ["добавить", "предлагаю", "не хватает"]):
        response = "Ловлю идею. Подумаем."
    else:
        response = "Принято. Спасибо за отзыв."

    await message.answer(f"{response} ({mode})\n\nЕсли хотите снова — возвращайтесь: {MAIN_BOT_LINK}")

    completed_users.add(user_id)
    user_mode.pop(user_id, None)

if name == '__main__':
    executor.start_polling(dp, skip_updates=True)
