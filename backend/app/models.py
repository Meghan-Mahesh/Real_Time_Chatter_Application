from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


# ===============================
# USER MODEL
# ===============================
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False)

    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)

    warning_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    sent_messages = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender"
    )

    received_messages = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver"
    )


# ===============================
# MESSAGE MODEL
# ===============================
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    room = Column(String, nullable=True)  # group chat

    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )

    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages"
    )
