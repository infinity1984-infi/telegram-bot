from pyrogram import Client, filters
import random

# Replace these with your actual credentials
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

# Replace with your media channel ID (can be username or ID)
MEDIA_CHANNEL = -1001234567890

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Command or text trigger
@app.on_message(filters.private & filters.text)
def send_random_video(client, message):
    try:
        number = int(message.text.strip())
        if 1 <= number <= 100:
            # Message ID and user text must match
            client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=MEDIA_CHANNEL,
                message_id=number  # media message ID in batch channel must match number
            )
        else:
            message.reply("⚠️ Please enter a number between 1 and 100.")
    except ValueError:
        message.reply("❌ Invalid input! Please send a number only.")

print("Bot is running...")
app.run()
