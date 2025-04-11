import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("FICE_QA_TELEGRAM_BOT_TOKEN")
CHAT_API_URL = os.getenv("FICE_QA_CHAT_API_URL")
