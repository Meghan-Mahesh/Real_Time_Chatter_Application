from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import json

from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ..auth.jwt import SECRET_KEY, ALGORITHM
from ..database import SessionLocal
from ..models import Message, User
from ..ml.bad_word_model import handle_bad_word

router = APIRouter()


# ===============================
# CONNECTION MANAGER
# ===============================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for ws in self.active_connections:
            await ws.send_text(json.dumps(message))


manager = ConnectionManager()


# ===============================
# WEBSOCKET ENDPOINT
# ===============================
@router.websocket("/chat/ws")
async def websocket_chat(websocket: WebSocket):
    # 1️⃣ token URL se nikalo
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return

    # 2️⃣ token verify
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if not username:
            await websocket.close()
            return
    except JWTError:
        await websocket.close()
        return

    # 3️⃣ connect
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            message_text = payload.get("text")

            # ✅ DB session per message
            with SessionLocal() as db:
                user = db.query(User).filter(User.username == username).first()
                if not user:
                    continue

                # 🚫 Blocked user
                if user.is_blocked:
                    await websocket.send_text(json.dumps({
                        "user": "System",
                        "text": "You are blocked and cannot send messages.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                    await websocket.close()
                    break

                # 🔎 Bad-word moderation
                moderation_response = handle_bad_word(user, message_text, db)
                if moderation_response:
                    if moderation_response["type"] == "warning":
                        await websocket.send_text(json.dumps({
                            "user": "System",
                            "text": moderation_response["message"],
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "alert": True
                        }))
                        continue
                    elif moderation_response["type"] == "block":
                        await websocket.send_text(json.dumps({
                            "user": "System",
                            "text": moderation_response["message"],
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "blocked": True
                        }))
                        await websocket.close()
                        break

                # ✅ Save message to DB
                db_message = Message(
                    sender_id=user.id,
                    content=message_text,
                    timestamp=datetime.now(timezone.utc)
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)

            # ✅ Broadcast message to all connections
            await manager.broadcast({
                "user": username,
                "text": message_text,
                "timestamp": db_message.timestamp.isoformat()
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"{username} disconnected")
