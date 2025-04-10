import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple
from pyrogram import Client, filters
from pyrogram.types import Message, User
from pyrogram.errors import (
    FloodWait, MessageIdInvalid, PeerIdInvalid,
    ChannelInvalid, ChatAdminRequired, UserNotParticipant
)

# ==================== CONFIGURATION ====================
# Bot API credentials (get from https://my.telegram.org)
API_ID = 23810894  # Replace with your API ID
API_HASH = "7f51292061e6a64df8589ae7756e5603"  # Replace with your API HASH
BOT_TOKEN = "7145224784:AAE-6hVmhm6fWcJMj-4mI0zKqHf2-fxXud8"  # Replace with your bot token

# Channel configuration
DEFAULT_BATCH_CHANNEL_ID = -1002610839118  # Your media channel ID
FORCE_SUB_CHANNEL_ID = 0  # Set to 0 to disable force sub

# Admin configuration (add your Telegram user ID)
ADMINS = frozenset({6285668838})  # Use frozenset for immutability and hashability

# Bot behavior settings
MAX_BATCH_SIZE = 50  # Maximum files in one batch request
REQUEST_DELAY = 1  # Seconds between requests to avoid flooding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== BOT CLASS ====================
class AllInOneMediaBot:
    def __init__(self):
        self.app = Client(
            "all_in_one_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True,
            workers=100,
            sleep_threshold=60
        )
        self.batch_channels = {DEFAULT_BATCH_CHANNEL_ID: DEFAULT_BATCH_CHANNEL_ID}
        self.force_sub_channels = {}
        if FORCE_SUB_CHANNEL_ID:
            self.force_sub_channels[DEFAULT_BATCH_CHANNEL_ID] = FORCE_SUB_CHANNEL_ID
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.on_message(filters.private & filters.text & filters.incoming)
        async def handle_message(client: Client, message: Message):
            await self.process_user_request(message)

        @self.app.on_message(filters.command("setbatch") & filters.user(ADMINS))
        async def set_batch_channel(client: Client, message: Message):
            """Set batch channel: Reply to channel message with /setbatch"""
            if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
                await message.reply("ℹ️ Reply to forwarded channel message with /setbatch")
                return
            channel = message.reply_to_message.forward_from_chat
            self.batch_channels[channel.id] = channel.id
            await message.reply(f"✅ Batch channel set to: {channel.title} (ID: {channel.id})")

        @self.app.on_message(filters.command("setforcesub") & filters.user(ADMINS))
        async def set_force_sub(client: Client, message: Message):
            """Set force sub channel: Reply to channel message with /setforcesub"""
            if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
                await message.reply("ℹ️ Reply to forwarded channel message with /setforcesub")
                return
            channel = message.reply_to_message.forward_from_chat
            self.force_sub_channels[channel.id] = channel.id
            await message.reply(f"✅ Force sub channel set to: {channel.title}")

        @self.app.on_message(filters.command("addadmin") & filters.user(ADMINS))
        async def add_admin(client: Client, message: Message):
            """Add admin: Reply to user's message with /addadmin"""
            if not message.reply_to_message or not message.reply_to_message.from_user:
                await message.reply("ℹ️ Reply to user's message with /addadmin")
                return
            user = message.reply_to_message.from_user
            ADMINS.add(user.id)  # Add admin to the global set
            await message.reply(f"✅ Added {user.first_name} as admin")

        @self.app.on_message(filters.command("removeadmin") & filters.user(ADMINS))
        async def remove_admin(client: Client, message: Message):
            """Remove admin: Reply to user's message with /removeadmin"""
            if not message.reply_to_message or not message.reply_to_message.from_user:
                await message.reply("ℹ️ Reply to user's message with /removeadmin")
                return
            user = message.reply_to_message.from_user
            if user.id in ADMINS:
                ADMINS.remove(user.id)  # Remove admin from the global set
                await message.reply(f"✅ Removed {user.first_name} from admins")
            else:
                await message.reply("⚠️ User is not an admin")

        @self.app.on_message(filters.command("batch") & filters.user(ADMINS))
        async def create_batch(client: Client, message: Message):
            """Create batch: Reply to first message with /batch"""
            if not message.reply_to_message:
                await message.reply(
                    "ℹ️ Reply to first message of batch with /batch\n"
                    "Example: Reply to message ID 2 (file #1) to start batch"
                )
                return
            try:
                start_id = message.reply_to_message.id
                messages = []
                current_id = start_id
                while len(messages) < MAX_BATCH_SIZE:
                    msg = await self.app.get_messages(message.chat.id, message_ids=current_id)
                    if msg.empty:
                        break
                    messages.append(msg)
                    current_id += 1
                await message.reply(
                    f"✅ Batch created with {len(messages)} files\n"
                    f"First ID: {start_id}\nLast ID: {current_id - 1}\n"
                    f"Users can request: {start_id}-{current_id - 1}"
                )
            except Exception as e:
                await message.reply(f"❌ Error creating batch: {e}")

    async def process_user_request(self, message: Message):
        user_id = message.from_user.id
        text = message.text.strip()

        # Check force subscription
        if await self.check_force_sub(message):
            return

        # Handle batch request (1-5 format)
        if '-' in text and len(text.split('-')) == 2:
            start, end = map(str.strip, text.split('-'))
            if start.isdigit() and end.isdigit():
                await self.handle_batch_request(message, int(start), int(end))
                return

        # Handle single number request
        if text.isdigit():
            await self.handle_single_request(message, int(text))
            return

        await message.reply(
            "📌 How to use:\n"
            "• Send number (e.g., 5) for single file\n"
            "• Send range (e.g., 3-7) for multiple files\n"
            "❌ Invalid input"
        )

    async def check_force_sub(self, message: Message) -> bool:
        if not self.force_sub_channels:
            return False
        user_id = message.from_user.id
        for channel_id in self.force_sub_channels.values():
            try:
                await self.app.get_chat_member(channel_id, user_id)
            except UserNotParticipant:
                invite = await self.app.create_chat_invite_link(channel_id, member_limit=1)
                await message.reply(
                    f"⚠️ Join our channel first:\n{invite.invite_link}\n"
                    "After joining, try again.",
                    disable_web_page_preview=True
                )
                return True
        return False

    async def handle_single_request(self, message: Message, num: int):
        if num < 1:
            await message.reply("⚠️ Number must be > 0")
            return
        loading = await message.reply(f"⏳ Fetching file #{num}...")
        try:
            msg = await self.app.get_messages(next(iter(self.batch_channels.values())), num)
            await self.send_media(message, msg, single=True)
        except Exception as e:
            await self.handle_error(loading, e)
        finally:
            await loading.delete()

    async def handle_batch_request(self, message: Message, start: int, end: int):
        if start < 1 or end < 1:
            await message.reply("⚠️ Numbers must be > 0")
            return
        if start > end:
            await message.reply("⚠️ First number should be smaller")
            return
        if (end - start + 1) > MAX_BATCH_SIZE:
            await message.reply(f"⚠️ Max batch size is {MAX_BATCH_SIZE} files")
            return
        loading = await message.reply(f"⏳ Preparing {start}-{end} ({end - start + 1} files)...")
        success = 0
        for num in range(start, end + 1):
            try:
                msg = await self.app.get_messages(next(iter(self.batch_channels.values())), num)
                await self.send_media(message, msg, single=False)
                success += 1
            except Exception as e:
                logger.error(f"Error in batch {num}: {e}")
        await loading.edit_text(f"✅ Batch complete\nSent: {success}/{end - start + 1} files")

    async def send_media(self, message: Message, source_msg: Message, single: bool):
        if source_msg.empty:
            raise MessageIdInvalid
        supported = (filters.video | filters.photo | filters.document | filters.text)
        if not supported(source_msg):
            raise ValueError("Unsupported media type")
        await source_msg.copy(
            chat_id=message.chat.id,
            caption=f"#{source_msg.id}\n{source_msg.caption or ''}" if single else None
        )
        await asyncio.sleep(REQUEST_DELAY)

    async def handle_error(self, message: Message, error: Exception):
        if isinstance(error, MessageIdInvalid):
            await message.edit("⚠️ Media not found")
        elif isinstance(error, FloodWait):
            wait = error.value
            await message.edit(f"⏳ Please wait {wait} seconds")
            await asyncio.sleep(wait)
        elif isinstance(error, (PeerIdInvalid, ChannelInvalid)):
            await message.edit("❌ Bot can't access channel")
        else:
            logger.error("Request failed", exc_info=error)
            await message.edit("❌ Error occurred")

    async def run(self):
        await self.app.start()
        me = await self.app.get_me()
        logger.info(f"Bot @{me.username} started")
        logger.info(f"Admins: {ADMINS}")
        logger.info(f"Batch channels: {self.batch_channels}")
        logger.info(f"Force sub channels: {self.force_sub_channels}")
        await asyncio.Event().wait()  # Run forever


if __name__ == "__main__":
    bot = AllInOneMediaBot()
    asyncio.run(bot.run())
