import logging
import requests
from config import settings

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.api_url = settings.CHAT_API_URL

    def query_chat(self, conversation: list) -> str:
        """
        Sends the conversation history to the FastAPI endpoint and returns the answer.

        Args:
            conversation (list): A list of conversation messages.

        Returns:
            str: The answer received from the API.

        Raises:
            Exception: If the HTTP request fails.
        """

        def query_chat(self, conversation: list) -> str:
            payload = {"conversation": conversation}
            try:
                response = requests.post(self.api_url, json=payload, timeout=10)
                response.raise_for_status()
                data = response.json()
                return data.get("answer", "Answer not received")
            except requests.Timeout:
                logger.error("Request to chat API timed out")
                raise Exception("Request timeout")
            except Exception as e:
                logger.exception("Error querying chat API: %s", e)
                raise
