import asyncio
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ====== ВЕБ-СЕРВЕР ДЛЯ ОБМАНА RENDER ======
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ====== ЧТЕНИЕ ПЕРЕМЕННЫХ ======
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
    await app.start()
    print("Бот успешно запущен!", flush=True)
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

