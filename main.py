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
    await message.answer("Salom! Menga YouTube, TikTok yoki Instagram havolasini yuboring.\nMen sizga qo'shiqni (MP3) yuklab beraman! 🎵")

@dp.message()
async def download_song(message: types.Message):
    url = message.text.strip() if message.text else ""
    
    if not url.startswith(("http://", "https://")):
        await message.answer("Iltimos, to'g'ri havola yuboring.")
        return

    status_msg = await message.answer("⏳ Yuklab olinmoqda, biroz kuting...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        # YouTube uchun muhim sozlamalar (2026)
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios'],
            }
        },
    }

    mp3_path = "song.mp3"

    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await asyncio.to_thread(download)

        if os.path.exists(mp3_path):
            audio = FSInputFile(mp3_path)
            await message.answer_audio(audio)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Fayl yaratilmadi. Qayta urinib ko'ring.")

    except Exception as e:
        error_text = str(e)
        logging.error(f"Xatolik: {error_text}")
        
        # Foydalanuvchiga tushunarli xabar
        if "Private video" in error_text or "private" in error_text.lower():
            await status_msg.edit_text("🔒 Bu video maxfiy (private). Yuklab bo'lmaydi.")
        elif "Video unavailable" in error_text:
            await status_msg.edit_text("❌ Video mavjud emas yoki o'chirib tashlangan.")
        elif "Sign in" in error_text or "cookies" in error_text.lower():
            await status_msg.edit_text("⚠️ YouTube blokladi. Keyinroq urinib ko'ring.")
        else:
            await status_msg.edit_text(
                "Kechirasiz, bu havoladan yuklab bo'lmadi.\n\n"
                "Sabab: video himoyalangan yoki server tomonidan cheklangan."
            )
    
    finally:
        if os.path.exists(mp3_path):
            try:
                os.remove(mp3_path)
            except:
                pass
        # Boshqa qoldiq fayllarni ham tozalash
        for f in os.listdir("."):
            if f.startswith("song.") and f != "song.mp3":
                try:
                    os.remove(f)
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
