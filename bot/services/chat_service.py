import logging
from typing import List, Dict

import requests
from config import settings

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.api_url = settings.CHAT_API_URL

    def query_chat(self, conversation: List[Dict[str, str]]) -> str:
        """
        Sends the conversation history to the FastAPI chat endpoint and returns the answer.

        Args:
            conversation (List[Dict[str, str]]): List of conversation messages with 'role' and 'content'.

        Returns:
            str: The answer received from the API.

        Raises:
            Exception: If the request fails, times out, or returns an invalid response.
        """
        try:
            response = requests.post(
                f'{self.api_url}/chat',
                json={"conversation": conversation},
                timeout=180
            )
            response.raise_for_status()
            return response.json()["answer"]
        except requests.Timeout:
            logger.error("Request to chat API timed out")
            raise Exception("Request timeout")
        except requests.RequestException as e:
            logger.exception("API request failed: %s", e)
            raise Exception(f"API request failed: {str(e)}")
        except (KeyError, ValueError) as e:
            logger.exception("Invalid API response: %s", e)
            raise Exception("Invalid API response")
