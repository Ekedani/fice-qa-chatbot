import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("FICE_QA_TELEGRAM_BOT_TOKEN")
CHAT_API_URL = os.getenv("FICE_QA_CHAT_API_URL")
DATABASE_URL = os.getenv("FICE_QA_CONVERSATION_DB_URL")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("FICE_QA_TELEGRAM_BOT_TOKEN must be set")

if not CHAT_API_URL:
    raise ValueError("FICE_QA_CHAT_API_URL must be set")

if not DATABASE_URL:
    raise ValueError("FICE_QA_CONVERSATION_DB_URL must be set")
