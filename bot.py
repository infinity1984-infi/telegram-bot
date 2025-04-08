import os
import sys
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
BATCH_CHANNEL_ID = int(os.getenv("BATCH_CHANNEL_ID"))

admin_users = set()

app = Client("direct-media-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply("👋 Welcome! Send a number to get your video.")

@app.on_message(filters.command("admin"))
async def admin_login(client, message):
    if len(message.command) < 2:
        await message.reply("❌ Please provide password: `/admin <password>`", quote=True)
        return
    password = message.command[1]
    if password == ADMIN_PASSWORD:
        admin_users.add(message.from_user.id)
        await message.reply("✅ Admin access granted.")
    else:
        await message.reply("❌ Wrong password.")

@app.on_message(filters.command("log"))
async def log_handler(client, message):
    if message.from_user.id not in admin_users:
        return await message.reply("❌ Unauthorized")
    await message.reply("📄 Log: All actions running fine!")

@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    if message.from_user.id not in admin_users:
        return await message.reply("❌ Unauthorized")
    await message.reply("📊 Stats: Bot is live and working!")

@app.on_message(filters.command("restart"))
async def restart_handler(client, message):
    if message.from_user.id not in admin_users:
        return await message.reply("❌ Unauthorized")
    await message.reply("🔄 Restarting bot...")
    os.execl(sys.executable, sys.executable, *sys.argv)

@app.on_message(filters.text & filters.private)
async def number_handler(client, message: Message):
    if not message.text.isdigit():
        return await message.reply("❌ Please send a valid number.")
    number = int(message.text)
    msg_id = number + 1
    try:
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=BATCH_CHANNEL_ID,
            message_id=msg_id
        )
    except Exception as e:
        await message.reply("❌ No video found for this number.")

app.run()
