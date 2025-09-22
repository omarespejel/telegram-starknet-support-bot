"""Minimal Starknet Telegram Group Bot."""

import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ai_client import StarknetAI
from config import (
    AI_API_BASE_URL,
    AI_API_WS_URL,
    BOT_USERNAME,
    RATE_LIMIT_PER_CHAT,
    RATE_LIMIT_WINDOW,
    SUPABASE_SERVICE_KEY,
    SUPABASE_URL,
    TELEGRAM_BOT_TOKEN,
)
from database import Database

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Validate required Telegram token at application start
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is required")

class BotMetrics:
    def __init__(self):
        self.total_messages = 0
        self.successful_responses = 0
        self.failed_responses = 0

    def log_message(self) -> None:
        self.total_messages += 1

    def log_success(self) -> None:
        self.successful_responses += 1

    def log_failure(self) -> None:
        self.failed_responses += 1


# Initialize components
db = Database(SUPABASE_URL, SUPABASE_SERVICE_KEY)
ai = StarknetAI(AI_API_BASE_URL, AI_API_WS_URL)
metrics = BotMetrics()


# Simple rate limiter
class RateLimiter:
    def __init__(self):
        self.requests: dict[str, list[datetime]] = {}

    def is_allowed(self, chat_id: str) -> bool:
        now = datetime.now()
        chat_id = str(chat_id)

        # Clean old requests
        if chat_id in self.requests:
            self.requests[chat_id] = [
                t
                for t in self.requests[chat_id]
                if now - t < timedelta(seconds=RATE_LIMIT_WINDOW)
            ]
        else:
            self.requests[chat_id] = []

        # Check limit
        if len(self.requests[chat_id]) >= RATE_LIMIT_PER_CHAT:
            return False

        self.requests[chat_id].append(now)
        return True


rate_limiter = RateLimiter()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Hi! I'm the Starknet Expert Bot.\n\n"
        "**In groups:** Mention me with @" + BOT_USERNAME + " to ask questions\n"
        "**In DMs:** Just send your question directly\n\n"
        "I can help with:\n"
        "• Cairo programming\n"
        "• Smart contracts\n"
        "• StarkNet architecture\n"
        "• Account abstraction\n"
        "• zk-STARKs",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "🤖 **Starknet Bot Help**\n\n"
        "**Commands:**\n"
        "/start - Initialize bot\n"
        "/help - This help message\n\n"
        "**Usage:**\n"
        "• In groups: @" + BOT_USERNAME + " your question\n"
        "• In DMs: Just type your question\n\n"
        "**Topics I know:**\n"
        "Cairo, smart contracts, StarkNet, L2 scaling, zk-STARKs",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    message = update.message
    chat = update.effective_chat
    user = update.effective_user

    # Check if in group and if bot was mentioned
    if chat.type in ["group", "supergroup"]:
        # Only respond if mentioned or replied to
        bot_username = f"@{BOT_USERNAME}"
        is_mentioned = bot_username in message.text
        is_reply_to_bot = (
            message.reply_to_message
            and message.reply_to_message.from_user.id == context.bot.id
        )

        if not (is_mentioned or is_reply_to_bot):
            return  # Ignore message

        # Clean the mention from text
        text = message.text.replace(bot_username, "").strip()
    else:
        # Direct message
        text = message.text

    # Count message and check rate limit
    metrics.log_message()
    if not rate_limiter.is_allowed(chat.id):
        await message.reply_text(
            "⚠️ Rate limit reached. Please wait a moment before asking again.",
            reply_to_message_id=message.message_id,
        )
        return

    # Show typing
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    try:
        # Save user message
        await db.save_message(
            user_id=str(user.id),
            chat_id=str(chat.id),
            chat_type=chat.type,
            username=user.username,
            message=text,
            role="user",
        )

        # Get chat history for context
        history = await db.get_chat_history(str(chat.id))

        # Get AI response
        response = await ai.get_response(
            message=text, chat_id=str(chat.id), history=history
        )

        # Send response
        if len(response) > 4000:
            # Split long responses
            parts = [response[i : i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.reply_text(
                    part, disable_web_page_preview=True
                )
        else:
            await message.reply_text(
                response,
                disable_web_page_preview=True,
                reply_to_message_id=(
                    message.message_id if chat.type in ["group", "supergroup"] else None
                ),
            )

        # Save bot response
        await db.save_message(
            user_id=str(context.bot.id),
            chat_id=str(chat.id),
            chat_type=chat.type,
            username=context.bot.username,
            message=response,
            role="assistant",
        )
        metrics.log_success()

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.reply_text(
            "Sorry, I encountered an error. Please try again.",
            reply_to_message_id=message.message_id,
        )
        metrics.log_failure()


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    logger.info(f"Starting bot @{BOT_USERNAME}...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
