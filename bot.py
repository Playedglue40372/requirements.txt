import sys
import subprocess

# 1. Автоматическая установка необходимых библиотек
required_libraries = ["aiohttp", "pyrogram", "tgcrypto"]
for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        print(f"Библиотека {lib} не найдена. Устанавливаю...", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

import asyncio
import os
import re
import multiprocessing
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ====== КОСТЫЛЬ ДЛЯ ПОРТА RENDER ======
async def handle_health(request):
    return web.Response(text="OK")

async def start_web_server():
    server = web.Application()
    server.add_routes([web.get("/", handle_health)])
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Веб-заглушка успешно заведена на порту {port}", flush=True)

# ====== НАСТРОЙКИ И ЛОГИКА БОТА ======
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

def keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📡 Получить прокси", callback_data="proxy")],
            [InlineKeyboardButton("🔄 Другой прокси", callback_data="proxy")],
        ]
    )

async def get_proxy(app):
    try:
        user = Client("proxy_user", api_id=API_ID, api_hash=API_HASH, workdir=".")
        await user.start()
    except Exception as e:
        print(f"Ошибка сессии юзербота: {e}. Пробую пересоздать...", flush=True)
        if os.path.exists("./proxy_user.session"):
            os.remove("./proxy_user.session")
        user = Client("proxy_user", api_id=API_ID, api_hash=API_HASH, workdir=".")
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
    return proxy if proxy else "Не удалось получить прокси"

# Функция, которая запустится в изолированном процессе
def run_bot_process():
    # Создаем чистый цикл событий внутри нового процесса
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workdir=".")

    @app.on_message(filters.command("start"))
    async def start(client, message):
        await message.reply("Нажми кнопку:", reply_markup=keyboard())

    @app.on_callback_query()
    async def callback(client, callback_query):
        if callback_query.data == "proxy":
            await callback_query.message.edit_text("⏳ Получаю прокси...")
            proxy = await get_proxy(app)
            await callback_query.message.reply(
                f"📡 Прокси:\n\n{proxy}", reply_markup=keyboard()
            )

    async def main():
        await start_web_server()
        await app.start()
        print("Бот успешно запущен в изолированном процессе!", flush=True)
        while True:
            await asyncio.sleep(3600)

    loop.run_until_complete(main())

if __name__ == "__main__":
    # Запускаем бота в отдельном независимом системном процессе
    bot_process = multiprocessing.Process(target=run_bot_process)
    bot_process.start()
    bot_process.join()

