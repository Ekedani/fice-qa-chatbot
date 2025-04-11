import os
import logging
from typing import List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config.settings import DATABASE_URL
from config.translations import Translations as t

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    def __init__(self):
        self.session_local = SessionLocal

    def reset_conversation(self, chat_id: int) -> None:
        session: Session = self.session_local()
        try:
            session.query(Conversation).filter(Conversation.chat_id == chat_id).delete()
            session.commit()
        except Exception as e:
            logger.exception(t.get('error_reset_conversation', 'uk') % {'chat_id': chat_id, 'error': str(e)})
            session.rollback()
        finally:
            session.close()

    def append_message(self, chat_id: int, message: Dict[str, Any]) -> None:
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
            logger.exception(t.get('error_append_message', 'uk') % {'chat_id': chat_id, 'error': str(e)})
            session.rollback()
        finally:
            session.close()

    def get_conversation(self, chat_id: int) -> List[Dict[str, Any]]:
        session: Session = self.session_local()
        try:
            records = (session.query(Conversation)
                       .filter(Conversation.chat_id == chat_id)  # Using proper SQLAlchemy comparison
                       .order_by(Conversation.timestamp.asc())
                       .all())
            conversation = [{"role": rec.role, "content": rec.content} for rec in records]
            return conversation
        except Exception as e:
            logger.exception(t.get('error_get_conversation', 'uk') % {'chat_id': chat_id, 'error': str(e)})
            return []
        finally:
            session.close()