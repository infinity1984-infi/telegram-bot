import os
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BATCH_CHANNEL_ID = int(os.getenv("BATCH_CHANNEL_ID"))

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & filters.text)
async def send_video(client, message):
    try:
        if not message.text.isdigit():
            await message.reply("❗ Please enter a valid number (1 to 100).")
            return

        num = int(message.text)
        if not 1 <= num <= 100:
            await message.reply("❗ Please enter a valid number (1 to 100).")
            return

        messages = await client.get_messages(BATCH_CHANNEL_ID, [num])
        if not messages or not messages[0].video:
            await message.reply("❗ No video found for that number.")
            return

        video_msg = messages[0]
        await message.reply_video(
            video=video_msg.video.file_id,
            caption=f"🎬 Here's your video: Episode {num}"
        )

    except PeerIdInvalid:
        await message.reply("❗ Bot isn't admin in batch channel. Please re-add the bot.")
    except Exception as e:
        await message.reply(f"❗ Failed to fetch video.\nError: `{e}`")

app.run()
