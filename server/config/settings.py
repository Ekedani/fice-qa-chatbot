import os

from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_URL = os.getenv("FICE_QA_DEEPSEEK_API_URL")
DEEPSEEK_API_KEY = os.getenv("FICE_QA_DEEPSEEK_API_KEY")
