from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_message_id = Column(String, unique=True, index=True)
    from_number = Column(String, index=True)
    message_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="received")  # received, processed, failed
    response_text = Column(Text, nullable=True)
    
class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True, index=True)
    webhook_type = Column(String, index=True)  # message, status, etc.
    payload = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # success, error
    error_message = Column(Text, nullable=True)
