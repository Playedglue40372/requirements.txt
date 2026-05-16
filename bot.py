import asyncio
import os
import re
import sys
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

# ====== ЧТЕНИЕ ПЕРЕМЕННЫХ ИЗ ПАНЕЛИ RENDER ======
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workdir=".")

def keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📡 Получить прокси", callback_data="proxy")],
            [InlineKeyboardButton("🔄 Другой прокси", callback_data="proxy")],
        ]
    )

async def get_proxy():
    # Защита от битого файла сессии: если файл поврежден, скрипт не упадет
    try:
        user = Client("proxy_user", api_id=API_ID, api_hash=API_HASH, workdir=".")
        await user.start()
    except Exception as e:
        print(f"Ошибка сессии юзербота: {e}. Пробую удалить старый файл сессии...", flush=True)
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
            f"📡 Прокси:\n\n{proxy}", reply_markup=keyboard()
        )

async def main():
    # Сначала запускаем веб-сервер для Render
    await start_web_server()
    # Затем запускаем основного бота
    await app.start()
    print("Бот успешно запущен и готов к работе!", flush=True)
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

