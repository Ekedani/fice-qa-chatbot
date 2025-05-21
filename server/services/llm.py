from langchain_deepseek import ChatDeepSeek
from core.config import get_settings
from functools import lru_cache


@lru_cache
def get_llm() -> ChatDeepSeek:
    settings = get_settings()
    return ChatDeepSeek(
        model="deepseek-chat",
        api_key=settings.deepseek_api_key,
        temperature=0.3,
        streaming=False,
    )
