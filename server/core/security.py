from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from core.config import get_settings

_api_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: str = Depends(_api_header)):
    settings = get_settings()
    # Check if the API key is provided
    # if key != settings.fice_api_key:
    #    raise HTTPException(status_code=401, detail="Unauthorized")
