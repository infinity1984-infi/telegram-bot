import os
from pyrogram import Client, filters
from pyrogram.errors import MessageIdInvalid, FloodWait
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BATCH_CHANNEL_ID = -1002610839118

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

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

app.run()
