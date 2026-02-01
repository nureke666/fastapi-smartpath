from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String) # "user" or "ai"
    content = Column(Text)
    context_topic = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Feedback
    is_liked = Column(Boolean, nullable=True) # None, True (like), False (dislike)
    
    user = relationship("User", back_populates="chat_messages")
