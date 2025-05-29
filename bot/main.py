import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import Command

from config.settings import TELEGRAM_BOT_TOKEN
from services.chat_service import ChatService
from services.conversation_service import ConversationService
from config.translations import Translations as t
from telegramify_markdown import markdownify

logger = logging.getLogger(__name__)
conversation_service = ConversationService(message_limit=4)
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
    chat_id = message.chat.id
    user_text = message.text.strip()
    loading_msg = None

    try:
        loading_msg = await message.answer_animation(
            animation="https://media1.tenor.com/m/uaLasm_ExBcAAAAd/a-parakeet-admiring-himself-parakeet.gif",
            caption="Бот шукає інформацію. Будь ласка, очікуйте на відповідь."
        )

        conversation_service.append_message(chat_id, {"role": "user", "content": user_text})
        conversation = conversation_service.get_conversation(chat_id)
        await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        raw_answer = chat_service.query_chat(conversation)
        conversation_service.append_message(chat_id, {"role": "assistant", "content": raw_answer})
        answer = markdownify(raw_answer)
        await message.answer(answer, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error processing message: %s", e)
        await message.answer(t.get('error'))

    finally:
        if loading_msg:
            await message.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)


if __name__ == "__main__":
    import asyncio

    bot = Bot(token=TELEGRAM_BOT_TOKEN)


    async def main():
        print("Bot is up and running")
        await dp.start_polling(bot)


    asyncio.run(main())
