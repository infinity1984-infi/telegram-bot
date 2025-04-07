from pyrogram import Client, filters
from pyrogram.types import Message
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Video links mapped to numbers
videos = {
    "1": "https://t.me/c/2610839118/3",
    "2": "https://t.me/c/2610839118/4",
    "3": "https://t.me/c/2610839118/5",
    "4": "https://t.me/c/2610839118/6",
    "5": "https://t.me/c/2610839118/7",
    "6": "https://t.me/c/2610839118/8",
    "7": "https://t.me/c/2610839118/9",
    "8": "https://t.me/c/2610839118/10",
    "9": "https://t.me/c/2610839118/11",
    "10": "https://t.me/c/2610839118/12"
}

@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("👋 Welcome!\nSend a number from 1 to 10 to receive a video.")

@bot.on_message(filters.text & filters.private)
async def send_video(_, message: Message):
    num = message.text.strip()
    if num in videos:
        await message.reply_video(videos[num])
    else:
        await message.reply("❗ Please enter a valid number (1 to 10).")

bot.run()
