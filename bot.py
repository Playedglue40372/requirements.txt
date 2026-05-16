from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import asyncio
import os

# ====== ДАННЫЕ (ВСТАВИШЬ САМ) ======
API_ID = int(os.getenv("33694427", "0"))
API_HASH = os.getenv("f819241c056f6827cc0188ff1479a7ce", "")
BOT_TOKEN = os.getenv("8822781449:AAHiz6Ufn2ju045iDs2YIhcsr4XAAM9urxE", "")

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 Получить прокси", callback_data="proxy")],
        [InlineKeyboardButton("🔄 Другой прокси", callback_data="proxy")]
    ])


async def get_proxy():
    user = Client(
        "proxy_user",
        api_id=API_ID,
        api_hash=API_HASH
    )

    await user.start()

    await user.send_message("TProxyRobot", "/start")
    await asyncio.sleep(2)

    await user.send_message("TProxyRobot", "Получить прокси")
    await asyncio.sleep(3)

    text = ""

    async for msg in user.get_chat_history("TProxyRobot", limit=5):
        if msg.text:
            text += msg.text + "\n"

    await user.stop()

    proxy = re.findall(r"\d+\.\d+\.\d+\.\d+:\d+", text)

    return proxy[0] if proxy else "Не удалось получить прокси"


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Нажми кнопку:", reply_markup=keyboard())


@app.on_callback_query()
async def callback(client, callback_query):
    if callback_query.data == "proxy":
        await callback_query.message.edit_text("⏳ Получаю прокси...")
        proxy = await get_proxy()

        await callback_query.message.reply(
            f"📡 Прокси:\n\n{proxy}",
            reply_markup=keyboard()
        )


app.run()