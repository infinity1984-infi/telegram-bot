from pyrogram import Client, filters
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BATCH_CHANNEL_ID = int(os.getenv("BATCH_CHANNEL_ID"))

bot = Client(
    "kin_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.private & filters.text)
async def send_video(client, message):
    if not message.text.isdigit():
        await message.reply("❗ Please send a number between 1 to 100.")
        return

    number = int(message.text)
    if 1 <= number <= 100:
        try:
            await message.reply_chat_action("upload_video")
            await message.copy(chat_id=message.chat.id, from_chat_id=BATCH_CHANNEL_ID, message_id=number)
        except Exception as e:
            await message.reply(f"❗ Failed to fetch video.\nError: {e}")
    else:
        await message.reply("❗ Please enter a valid number (1 to 100).")

bot.run()
