import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config.settings import TELEGRAM_BOT_TOKEN
from services.chat_service import ChatService
from services.conversation_service import ConversationService
from config.translations import Translations as t

logger = logging.getLogger(__name__)
conversation_service = ConversationService()
chat_service = ChatService()

dp = Dispatcher()


@dp.message(Command("start"))
async def start_command(message: types.Message) -> None:
    """
    Handles the /start command.
    Resets the conversation history and sends a welcome message.
    """
    chat_id = message.chat.id
    conversation_service.reset_conversation(chat_id)
    await message.answer(t.get('start'))


@dp.message(Command("help"))
async def help_command(message: types.Message) -> None:
    """
    Handles the /help command.
    Sends a help message.
    """
    await message.answer(t.get('help'))


@dp.message(Command("reset"))
async def reset_command(message: types.Message) -> None:
    """
    Handles the /reset command.
    Resets the conversation history.
    """
    chat_id = message.chat.id
    conversation_service.reset_conversation(chat_id)
    await message.answer(t.get('reset'))


@dp.message()
async def handle_message(message: types.Message) -> None:
    """
    Handles incoming text messages.
    Stores the user message, queries the chat API, stores the bot's reply, and sends the answer back.
    """
    chat_id = message.chat.id
    user_text = message.text.strip()

    try:
        conversation_service.append_message(chat_id, {"role": "user", "content": user_text})
        conversation = conversation_service.get_conversation(chat_id)
        answer = chat_service.query_chat(conversation)
        conversation_service.append_message(chat_id, {"role": "system", "content": answer})
        await message.answer(answer)
    except Exception as e:
        logger.exception("Error processing message: %s", e)
        await message.answer(t.get('error'))


if __name__ == "__main__":
    import asyncio

    bot = Bot(token=TELEGRAM_BOT_TOKEN)


    async def main():
        await dp.start_polling(bot)


    asyncio.run(main())
