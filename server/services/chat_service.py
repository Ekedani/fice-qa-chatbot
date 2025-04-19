from abc import ABC, abstractmethod
from typing import List
from models.chat_models import Message


class ChatService(ABC):
    """
    Abstract base class for chat services. Can be extended to integrate different LLM backends.
    """

    @abstractmethod
    async def get_answer(self, conversation: List[Message]) -> str:
        """
        Generate a response based on the conversation history.

        :param conversation: List of Message objects representing chat history
        :return: Generated response as a string
        """
        pass
