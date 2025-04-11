import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.chat_service import ChatService
from services.coversation_service import ConversationService

logger = logging.getLogger(__name__)
conversation_service = ConversationService()
chat_service = ChatService()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command.
    Resets the conversation history and sends a welcome message.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Callback context.
    """
    chat_id = update.effective_chat.id
    conversation_service.reset_conversation(chat_id)
    await update.message.reply_text("Hello! I am your bot. Send me a message and I'll reply using our RAG system.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /help command.
    Sends a help message.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Callback context.
    """
    await update.message.reply_text("Simply send a message. Use /reset to clear the conversation history.")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /reset command.
    Resets the conversation history.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Callback context.
    """
    chat_id = update.effective_chat.id
    conversation_service.reset_conversation(chat_id)
    await update.message.reply_text("Conversation history has been cleared.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles incoming text messages.
    Stores the user message, queries the chat API, stores the bot's reply, and sends the answer back.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Callback context.
    """
    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()

    conversation_service.append_message(chat_id, {"role": "user", "content": user_text})
    conversation = conversation_service.get_conversation(chat_id)

    try:
        answer = chat_service.query_chat(conversation)
    except Exception as e:
        logger.exception("Error querying chat API: %s", e)
        await update.message.reply_text("Sorry, an error occurred while processing your request.")
        return

    conversation_service.append_message(chat_id, {"role": "assistant", "content": answer})
    await update.message.reply_text(answer)
