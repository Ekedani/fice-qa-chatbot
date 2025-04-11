import os
import logging
from typing import List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config.translations import _

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "conversation.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(bind=engine)


class ConversationService:
    """
    Service for managing conversation history using SQLAlchemy ORM.
    """

    def __init__(self):
        self.session_local = SessionLocal

    def reset_conversation(self, chat_id: int) -> None:
        """
        Resets the conversation for the given chat by deleting all related messages.

        Args:
            chat_id (int): The chat ID.
        """
        session: Session = self.session_local()
        try:
            session.query(Conversation).filter(Conversation.chat_id == chat_id).delete()
            session.commit()
        except Exception as e:
            logger.exception(_("Error resetting conversation for chat_id %s: %s"), chat_id, e)
            session.rollback()
        finally:
            session.close()

    def append_message(self, chat_id: int, message: Dict[str, Any]) -> None:
        """
        Appends a message to the conversation stored in the SQLite database.

        Args:
            chat_id (int): The chat ID.
            message (dict): A dictionary containing the keys "role" and "content".
        """
        session: Session = self.session_local()
        try:
            record = Conversation(
                chat_id=chat_id,
                role=message.get("role", "unknown"),
                content=message.get("content", "")
            )
            session.add(record)
            session.commit()
        except Exception as e:
            logger.exception(_("Error appending message for chat_id %s: %s"), chat_id, e)
            session.rollback()
        finally:
            session.close()

    def get_conversation(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the conversation history for a given chat.

        Args:
            chat_id (int): The chat ID.

        Returns:
            List[dict]: A list of messages with "role" and "content" keys.
        """
        session: Session = self.session_local()
        try:
            records = (session.query(Conversation)
                       .filter(Conversation.chat_id == chat_id)
                       .order_by(Conversation.timestamp.asc())
                       .all())
            conversation = [{"role": rec.role, "content": rec.content} for rec in records]
            return conversation
        except Exception as e:
            logger.exception(_("Error retrieving conversation for chat_id %s: %s"), chat_id, e)
            return []
        finally:
            session.close()
