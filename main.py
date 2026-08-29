import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiohttp import web
import yt_dlp

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN environment variable is missing!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga YouTube havolasini yuboring, men sizga qo'shiqni yuklab beraman! 🎵")

@dp.message()
async def download_song(message: types.Message):
    url = message.text.strip() if message.text else ""
    
    if not url.startswith(("http://", "https://")):
        await message.answer("Iltimos, to'g'ri YouTube havolasini yuboring.")
        return

    status_msg = await message.answer("⏳ Qo'shiq yuklab olinmoqda, biroz kuting...")

    # Fayl nomi doimiy bo'lsin
    output_template = "song.%(ext)s"

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        'noplaylist': True,
    }

    mp3_path = "song.mp3"

    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return mp3_path

        # Yuklab olish (bloklovchi operatsiyani thread ga chiqaramiz)
        await asyncio.to_thread(download)

        if os.path.exists(mp3_path):
            audio = FSInputFile(mp3_path)
            await message.answer_audio(audio)
            await status_msg.delete()
        else:
            await status_msg.edit_text("Xatolik: mp3 fayl yaratilmadi.")

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await status_msg.edit_text("Kechirasiz, bu havoladan qo'shiqni yuklab bo'lmadi.\n\nSabab: video mavjud emas yoki yuklab olish mumkin emas.")
    
    finally:
        # Faylni o'chirish
        if os.path.exists(mp3_path):
            try:
                os.remove(mp3_path)
            except:
                pass

# Render uchun veb-server
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
