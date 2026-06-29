from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Message, User

router = APIRouter()

@router.get("/messages")
def get_messages(db: Session = Depends(get_db)):
    messages = (
        db.query(Message, User.username)
        .join(User, Message.sender_id == User.id)
        .order_by(Message.id.asc())
        .all()
    )

    return [
        {
            "user": username,
            "text": msg.content,
            "timestamp": msg.timestamp
        }
        for msg, username in messages
    ]
