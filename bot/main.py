import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import settings
from handlers import start, help_command, reset_command, handle_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Starts the Telegram bot using long polling.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("FICE_QA_TELEGRAM_BOT_TOKEN is not set in the environment variables.")
        return

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
