from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 23810894
API_HASH = "7f51292061e6a64df8589ae7756e5603"
BOT_TOKEN = "7145224784:AAE-6hVmhm6fWcJMj-4mI0zKqHf2-fxXud8"
BATCH_CHANNEL = -1002610839118  # Always use -100 before channel ID

# Mapping numbers (1 to 10) to message IDs (videos start from message ID 3)
VIDEO_IDS = {
    1: 3,
    2: 4,
    3: 5,
    4: 6,
    5: 7,
    6: 8,
    7: 9,
    8: 10,
    9: 11,
    10: 12,
}

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("👋 Welcome!\nSend a number from 1 to 10 and I'll send you the video.")

@app.on_message(filters.text & filters.private)
async def send_video(client, message: Message):
    try:
        num = int(message.text.strip())
        if num in VIDEO_IDS:
            msg_id = VIDEO_IDS[num]
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=BATCH_CHANNEL,
                message_id=msg_id
            )
        else:
            await message.reply("❗Please enter a number between 1 and 10.")
    except:
        await message.reply("❗Please enter a valid number (1 to 10).")

app.run()
