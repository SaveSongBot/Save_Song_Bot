import os
import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiohttp import web
import yt_dlp

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable is missing!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==================== SOZLAMALAR ====================

def get_audio_opts():
    return {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'media.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'retries': 5,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
            }
        },
    }

def get_video_opts():
    return {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'outtmpl': 'media.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'retries': 5,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
            }
        },
    }

def is_valid_url(text: str) -> bool:
    return bool(re.match(r'https?://', text.strip()))

def clean_files():
    for file in os.listdir("."):
        if file.startswith("media."):
            try:
                os.remove(file)
            except:
                pass

# ==================== KOMANDALAR ====================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎵 <b>SaveSongBot</b> — Eng zo'r yuklovchi bot\n\n"
        "Quyidagi platformalardan havola yuboring:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Instagram\n\n"
        "Keyin <b>Musiqa</b> yoki <b>Video</b> ni tanlang.",
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📖 <b>Qanday ishlatiladi?</b>\n\n"
        "1. Video havolasini yuboring\n"
        "2. <b>🎵 Musiqa</b> yoki <b>🎬 Video</b> tugmasini bosing\n"
        "3. Bot yuklab beradi\n\n"
        "Qo'llab-quvvatlanadi:\n"
        "✅ YouTube\n✅ TikTok\n✅ Instagram",
        parse_mode="HTML"
    )

# ==================== HAVOLA QABUL QILISH ====================

@dp.message(F.text)
async def handle_url(message: types.Message):
    url = message.text.strip()

    if not is_valid_url(url):
        await message.
