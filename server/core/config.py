from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str
    deepseek_api_key: str
    chroma_directory: str
    chroma_collection: str
    hf_model: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="fice_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
