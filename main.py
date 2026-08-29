import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import yt_dlp

TOKEN = "8860577089:AAFq0fEZ7zlhHF3I6BdA7izCaufQM1OMOZg"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Assalomu alaykum! 🤍\n"
        "Menga YouTube, Instagram yoki TikTok havolasini yuboring, "
        "men sizga yuklab beraman!"
    )

@dp.message()
async def download_media(message: Message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        await message.answer("Itimos, to‘g‘ri keladigan havola (link) yuboring! 🔗")
        return

    processing_msg = await message.answer("⏳ Yuklab olinmoqda, biroz kuting...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,
    }

    os.makedirs("downloads", exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await message.answer_video(types.FSInputFile(file_path), caption="Mana sizning videongiz! ✨ @Save_Song_Bot")
        
        os.remove(file_path)
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("❌ Kechirasiz, bu havoladan videoni yuklab bo‘lmadi.")
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        except:
            pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
