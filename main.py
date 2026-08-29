import os
import asyncio
import logging
import re
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

# ==================== YORDAMCHI FUNKSIYALAR ====================

def is_valid_url(text: str) -> bool:
    return bool(re.match(r'https?://', text.strip()))

def get_ydl_opts():
    """Eng barqaror sozlamalar"""
    return {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'retries': 3,
        'fragment_retries': 3,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
                'player_skip': ['webpage'],
            }
        },
        # Ba'zi bloklarni chetlab o'tish uchun
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

# ==================== KOMANDALAR ====================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎵 <b>SaveSongBot</b> ga xush kelibsiz!\n\n"
        "Menga quyidagi platformalardan havola yuboring:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Instagram\n\n"
        "Men sizga eng yaxshi sifatdagi <b>MP3</b> ni yuklab beraman.",
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📖 <b>Yordam</b>\n\n"
        "Shunchaki video havolasini yuboring.\n"
        "Bot avtomatik ravishda musiqani yuklab beradi.\n\n"
        "Qo'llab-quvvatlanadigan platformalar:\n"
        "✅ YouTube\n"
        "✅ TikTok\n"
        "✅ Instagram\n\n"
        "Muammo bo'lsa — qayta yuboring yoki biroz kutib turing.",
        parse_mode="HTML"
    )

# ==================== ASOSIY YUKLAB OLISH ====================

@dp.message()
async def download_song(message: types.Message):
    url = message.text.strip() if message.text else ""

    if not is_valid_url(url):
        await message.answer("Iltimos, to'g'ri havola (YouTube, TikTok yoki Instagram) yuboring.")
        return

    status = await message.answer("⏳ <b>Yuklab olinmoqda...</b>\nBiroz kuting.", parse_mode="HTML")

    ydl_opts = get_ydl_opts()
    mp3_path = "song.mp3"
    title = "Unknown Song"

    try:
        def download():
            nonlocal title
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown Song')
                # Ba'zi hollarda title juda uzun bo'lishi mumkin
                if len(title) > 60:
                    title = title[:57] + "..."

        await asyncio.to_thread(download)

        if os.path.exists(mp3_path):
            audio = FSInputFile(mp3_path, filename=f"{title}.mp3")
            await message.answer_audio(
                audio=audio,
                title=title,
                performer="SaveSongBot"
            )
            await status.delete()
        else:
            await status.edit_text("❌ Fayl yaratilmadi. Qayta urinib ko'ring.")

    except Exception as e:
        error = str(e).lower()
        logging.error(f"Xatolik: {e}")

        if "private" in error:
            text = "🔒 Bu video maxfiy (private). Yuklab bo'lmaydi."
        elif "unavailable" in error or "not available" in error:
            text = "❌ Video mavjud emas yoki o'chirib tashlangan."
        elif "sign in" in error or "login" in error or "cookies" in error:
            text = "⚠️ YouTube blokladi. Keyinroq urinib ko'ring."
        elif "blocked" in error or "403" in error:
            text = "🚫 Server IP si bloklangan. Keyinroq qayta urinib ko'ring."
        else:
            text = "❌ Yuklab bo'lmadi.\nSabab: video himoyalangan yoki vaqtincha muammo."

        await status.edit_text(text)

    finally:
        # Tozalash
        for file in os.listdir("."):
            if file.startswith("song."):
                try:
                    os.remove(file)
                except:
                    pass

# ==================== RENDER UCHUN WEB SERVER ====================

async def handle(request):
    return web.Response(text="SaveSongBot is running!")

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
