import os
from pyrogram import Client, filters
from pyrogram.errors import MessageIdInvalid, FloodWait
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BATCH_CHANNEL_ID = -1002610839118

app = Client(
    session_name=os.path.join("/mnt/data", "direct-media-bot"),
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.text)
async def handle_message(client, message):
    if not message.text.isdigit():
        await message.reply_text("❌ Please send a number like '1', '2', etc.")
        return

    msg_num = int(message.text)
    real_msg_id = msg_num + 1  # Because 1 maps to message_id 2 in batch channel

    try:
        msg = await client.get_messages(BATCH_CHANNEL_ID, message_ids=real_msg_id)
        if msg.video:
            await msg.copy(chat_id=message.chat.id)
        elif msg.text or msg.photo or msg.document:
            await msg.copy(chat_id=message.chat.id)
        else:
            await message.reply_text("❌ Media type not supported.")
    except MessageIdInvalid:
        await message.reply_text("⚠️ No video found for that number.")
    except FloodWait as e:
        await message.reply_text(f"⏳ Rate limited. Please wait {e.value} seconds.")
        await asyncio.sleep(e.value)
    except Exception as e:
        await message.reply_text(f"❌ Unexpected error: {e}")

import asyncio
from pyrogram.errors import FloodWait

while True:
    try:
        app.run()
        break  # Exit the loop if successful
    except FloodWait as e:
        wait_time = e.value + 5  # Add a buffer
        print(f"⚠️ FloodWait! Waiting {wait_time} seconds before retrying...")
        asyncio.run(asyncio.sleep(wait_time))
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        break
