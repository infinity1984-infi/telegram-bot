from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 23810894
API_HASH = "7f51292061e6a64df8589ae7756e5603"
BOT_TOKEN = "7145224784:AAE-6hVmhm6fWcJMj-4mI0zKqHf2-fxXud8"
BATCH_CHANNEL_ID = -1002610839118  # Add -100 before your batch channel ID

app = Client(
    "video_fetch_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "👋 Welcome!\nSend a number from 1 to 100 and I'll send you the video."
    )

@app.on_message(filters.private & filters.text)
async def send_video(client, message: Message):
    try:
        number = int(message.text.strip())
        if 1 <= number <= 100:
            messages = [msg async for msg in client.get_chat_history(BATCH_CHANNEL_ID, limit=200)]
            for msg in messages:
                if msg.caption and msg.caption.strip() == str(number):
                    await msg.copy(chat_id=message.chat.id)
                    return
            await message.reply_text("❌ Video not found for this number.")
        else:
            await message.reply_text("⚠️ Please send a number between 1 and 100.")
    except ValueError:
        await message.reply_text("❗ Please enter a valid number.")

app.run()
