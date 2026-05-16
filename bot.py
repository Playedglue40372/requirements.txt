import asyncio
import os
import re
import sys
from telethon import TelegramClient, events

# ====== ЧТЕНИЕ ПЕРЕМЕННЫХ ИЗ ПАНЕЛИ RENDER ======
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Создаем основного бота и юзербота через Telethon
bot = TelegramClient("my_bot_session", API_ID, API_HASH)
user = TelegramClient("proxy_user", API_ID, API_HASH)


# Кнопки для получения прокси
def get_keyboard():
    from telethon import Button

    return [
        [Button.inline("📡 Получить прокси", data="proxy")],
        [Button.inline("🔄 Другой прокси", data="proxy")],
    ]


# Обработка команды /start
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond("Нажми кнопку:", buttons=get_keyboard())


# Обработка нажатия на кнопки
@bot.on(events.CallbackQuery(data="proxy"))
async def callback(event):
    await event.edit("⏳ Получаю прокси...")

    try:
        # Запускаем юзербота для отправки команды донору
        if not user.is_connected():
            await user.connect()

        await user.send_message("TProxyRobot", "/start")
        await asyncio.sleep(2)
        await user.send_message("TProxyRobot", "Получить прокси")
        await asyncio.sleep(3)

        text = ""
        async for msg in user.iter_messages("TProxyRobot", limit=5):
            if msg.text:
                text += msg.text + "\n"

        proxy = re.findall(r"\d+\.\d+\.\d+\.\d+:\d+", text)
        result = proxy[0] if proxy else "Не удалось получить прокси"

    except Exception as e:
        result = f"Ошибка получения прокси: {e}"

    await event.respond(f"📡 Прокси:\n\n{result}", buttons=get_keyboard())


async def main():
    # Запускаем бота и держим его активным
    await bot.start(bot_token=BOT_TOKEN)
    print("Бот успешно запущен на Telethon!", flush=True)
    await bot.run_until_disconnected()


if __name__ == "__main__":
    # Жестко привязываем event loop, чтобы Linux на Render не ругался
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(main())

