import logging
from contextlib import contextmanager
from typing import List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


Base.metadata.create_all(bind=engine)


class ConversationService:
    def __init__(self, message_limit: int = 10):
        """
        Initializes the service with a _SessionLocal factory.
        """
        self._session_local = _SessionLocal
        self._message_limit = message_limit

    @contextmanager
    def session_scope(self) -> Session:
        """
        Provides a transactional scope around operations.

        Yields:
            Session: The active SQLAlchemy session.
        """
        session: Session = self._session_local()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def reset_conversation(self, chat_id: int) -> None:
        """
        Deletes all conversation records for the specified chat ID.

        Args:
            chat_id (int): The identifier for the conversation records.
        """
        try:
            with self.session_scope() as session:
                session.query(Conversation).filter(Conversation.chat_id == chat_id).delete()
        except Exception as e:
            logger.exception(
                'Failed to reset conversation: chat_id=%s, error=%s', chat_id, str(e)
            )

    def append_message(self, chat_id: int, message: Dict[str, Any]) -> None:
        """
        Appends a new message to the conversation.

        Args:
            chat_id (int): The chat ID to associate with this message.
            message (Dict[str, Any]): A dictionary containing 'role' and 'content' fields.
        """
        try:
            with self.session_scope() as session:
                count = session.query(Conversation).filter(
                    Conversation.chat_id == chat_id
                ).count()

                if count >= self._message_limit:
                    oldest_messages = session.query(Conversation).filter(
                        Conversation.chat_id == chat_id
                    ).order_by(
                        Conversation.timestamp.asc()
                    ).limit(count - self._message_limit + 1).all()

                    for msg in oldest_messages:
                        session.delete(msg)

                record = Conversation(
                    chat_id=chat_id,
                    role=message.get("role", "unknown"),
                    content=message.get("content", "")
                )
                session.add(record)
        except Exception as e:
            logger.exception(
                'Failed to append message for chat_id=%s with error=%s', chat_id, str(e)
            )

    def get_conversation(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all messages for the specified chat ID, sorted by timestamp.

        Args:
            chat_id (int): The identifier for the conversation.

        Returns:
            List[Dict[str, Any]]: A list of messages with 'role' and 'content'.
        """
        try:
            with self.session_scope() as session:
                records = (session.query(Conversation)
                           .filter(Conversation.chat_id == chat_id)
                           .order_by(Conversation.timestamp.asc())
                           .all())
                conversation = [{"role": rec.role, "content": rec.content} for rec in records]
                return conversation
        except Exception as e:
            logger.exception(
                'Failed to get conversation: chat_id=%s, error=%s', chat_id, str(e)
            )
            return []
