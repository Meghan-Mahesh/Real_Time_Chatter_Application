from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from typing import Annotated, Optional
from uuid import uuid4
from datetime import datetime
import os
import json

from app.websocket_manager import ConnectionManager
from app.models import (
    RegisteredUsers,
    ActiveUsers,
    Messages,
    CreateUser,
    LoginUser,
    ChangePasswordRequest
)
from app.auth import hash_password, verify_password
from app.database import create_tables_database, BASE_DIR, get_session


UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_database()
    yield

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

manager = ConnectionManager()


# ======================================================
# BASIC ROUTES
# ======================================================

@app.get("/")
async def serve_login():
    return FileResponse("app/static/login.html")


# ======================================================
# REGISTER
# ======================================================

@app.post("/register")
async def register(session: SessionDep, user: CreateUser):

    existing = session.exec(
        select(RegisteredUsers).where(RegisteredUsers.email == user.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = RegisteredUsers(
        user_name=user.user_name,
        email=user.email,
        pass_hash=hash_password(user.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "User registered successfully"}


# ======================================================
# LOGIN (Single Active Session Enforcement)
# ======================================================

@app.post("/login")
async def login(session: SessionDep, user: LoginUser):

    existing_user = session.exec(
        select(RegisteredUsers).where(RegisteredUsers.email == user.email)
    ).first()

    if not existing_user:
        raise HTTPException(status_code=400, detail="User does not exist")

    if not verify_password(user.password, existing_user.pass_hash):
        raise HTTPException(status_code=400, detail="Password incorrect")

    # 🔥 Enforce single active session
    existing_session = session.exec(
        select(ActiveUsers).where(
            ActiveUsers.user_id == existing_user.user_id
        )
    ).first()

    if existing_session:
        old_token = existing_session.token

        # Close old websocket if connected
        if old_token in manager.active_connections:
            old_ws = manager.active_connections[old_token]
            await old_ws.close(code=4001)
            del manager.active_connections[old_token]

        session.delete(existing_session)
        session.commit()

    token = str(uuid4())

    active = ActiveUsers(
        token=token,
        user_id=existing_user.user_id
    )

    session.add(active)
    session.commit()

    return {
        "message": "Login successful",
        "token": token,
        "user_name": existing_user.user_name,
        "email": existing_user.email,
        "profile_pic": existing_user.profile_pic
    }


# ======================================================
# ACTIVE USERS
# ======================================================

@app.get("/active-users")
async def get_active_users(session: SessionDep):

    users = session.exec(
        select(ActiveUsers, RegisteredUsers)
        .join(RegisteredUsers, ActiveUsers.user_id == RegisteredUsers.user_id)
    ).all()

    return [
        {
            "user_id": user.user_id,
            "user_name": user.user_name
        }
        for active, user in users
    ]


# ======================================================
# CHAT HISTORY (Public + Private)
# ======================================================

@app.get("/chat-history/{token}")
async def get_chat_history(
    session: SessionDep,
    token: str,
    user_id: Optional[int] = None
):

    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401, detail="Invalid session")

    current_user_id = active.user_id

    # PUBLIC CHAT
    if user_id is None:
        chats = session.exec(
            select(Messages, RegisteredUsers)
            .join(RegisteredUsers, Messages.sender_id == RegisteredUsers.user_id)
            .where(Messages.receiver_id == None)
            .order_by(Messages.timestamp)
        ).all()

    # PRIVATE CHAT
    else:
        chats = session.exec(
            select(Messages, RegisteredUsers)
            .join(RegisteredUsers, Messages.sender_id == RegisteredUsers.user_id)
            .where(
                (
                    (Messages.sender_id == current_user_id) &
                    (Messages.receiver_id == user_id)
                ) |
                (
                    (Messages.sender_id == user_id) &
                    (Messages.receiver_id == current_user_id)
                )
            )
            .order_by(Messages.timestamp)
        ).all()

    return [
        {
            "message_id": msg.message_id,
            "timestamp": str(msg.timestamp),
            "sender_id": user.user_id,
            "sender_name": user.user_name,
            "receiver_id": msg.receiver_id,
            "message": msg.message,
            "is_deleted": msg.is_deleted,
            "is_edited": msg.is_edited
        }
        for msg, user in chats
    ]



# ======================================================
# WEBSOCKET (Public + Private Messaging)
# ======================================================

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, session: SessionDep):

    active_user = session.get(ActiveUsers, token)

    if not active_user:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, token)

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            message_text = payload.get("message")
            receiver_id = payload.get("receiver_id")

            if not message_text:
                continue

            # 🔥 Create message
            chat = Messages(
                sender_id=active_user.user_id,
                receiver_id=receiver_id,
                message=message_text
            )

            session.add(chat)
            session.commit()
            session.refresh(chat)

            sender = session.get(RegisteredUsers, active_user.user_id)

            # 🔥 Check if receiver online (DELIVERED)
            is_delivered = False

            if receiver_id:
                receiver_session = session.exec(
                    select(ActiveUsers).where(
                        ActiveUsers.user_id == receiver_id
                    )
                ).first()

                if receiver_session:
                    is_delivered = True
                    chat.is_delivered = True
                    session.commit()

            # 🔥 Build formatted payload
            formatted_payload = {
                "message_id": chat.message_id,
                "timestamp": str(chat.timestamp),
                "sender_id": sender.user_id,
                "sender_name": sender.user_name,
                "receiver_id": receiver_id,
                "message": chat.message,
                "is_deleted": chat.is_deleted,
                "is_edited": chat.is_edited,
                "is_delivered": chat.is_delivered,
                "is_seen": chat.is_seen
            }

            # ============================
            # PRIVATE MESSAGE FLOW
            # ============================
            if receiver_id:

                # Send to receiver (if online)
                receiver_session = session.exec(
                    select(ActiveUsers).where(
                        ActiveUsers.user_id == receiver_id
                    )
                ).first()

                if receiver_session:
                    receiver_token = receiver_session.token

                    if receiver_token in manager.active_connections:
                        await manager.active_connections[receiver_token].send_text(
                            json.dumps(formatted_payload)
                        )

                # Send back to sender
                await websocket.send_text(json.dumps(formatted_payload))

            # ============================
            # PUBLIC MESSAGE FLOW
            # ============================
            else:
                await manager.broadcast(json.dumps(formatted_payload))

    except WebSocketDisconnect:
        await manager.disconnect(websocket)

        existing = session.get(ActiveUsers, token)
        if existing:
            session.delete(existing)
            session.commit()




# ======================================================
# PROFILE PICTURE
# ======================================================

@app.post("/upload-profile-pic/{token}")
async def upload_profile_pic(session: SessionDep, token: str, file: UploadFile = File(...)):

    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401)

    user = session.get(RegisteredUsers, active.user_id)

    filename = f"{user.user_id}.jpg"
    file_path = os.path.join(BASE_DIR, "static", "uploads", filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    profile_pic_path = f"/static/uploads/{filename}"
    user.profile_pic = profile_pic_path
    session.commit()

    return {"profile_pic": profile_pic_path}


# ======================================================
# CHANGE PASSWORD
# ======================================================

@app.post("/change-password/{token}")
async def change_password(token: str, data: ChangePasswordRequest, session: SessionDep):

    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401)

    user = session.get(RegisteredUsers, active.user_id)

    if not verify_password(data.old_password, user.pass_hash):
        raise HTTPException(status_code=400, detail="Old password incorrect")

    user.pass_hash = hash_password(data.new_password)
    session.commit()

    return {"message": "Password changed successfully"}

@app.put("/edit-message/{token}/{message_id}")
async def edit_message(
    token: str,
    message_id: int,
    new_text: str,
    session: SessionDep
):
    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401)

    message = session.get(Messages, message_id)
    if not message:
        raise HTTPException(status_code=404)

    if message.sender_id != active.user_id:
        raise HTTPException(status_code=403)

    message.message = new_text
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    session.commit()

    # 🔥 Broadcast edit event
    update_payload = {
        "type": "edit",
        "message_id": message.message_id,
        "new_text": message.message,
        "is_edited": True
    }

    await manager.broadcast(json.dumps(update_payload))

    return {"message": "Message updated"}



@app.delete("/delete-message/{token}/{message_id}")
async def delete_message(token: str, message_id: int, session: SessionDep):

    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401)

    message = session.get(Messages, message_id)
    if not message:
        raise HTTPException(status_code=404)

    if message.sender_id != active.user_id:
        raise HTTPException(status_code=403)

    message.is_deleted = True
    message.message = "This message was deleted"

    session.commit()
    update_payload = {
        "type": "delete",
        "message_id": message.message_id
    }

    await manager.broadcast(json.dumps(update_payload))

    return {"message": "Deleted"}

@app.put("/mark-seen/{token}/{user_id}")
async def mark_seen(token: str, user_id: int, session: SessionDep):

    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401)

    messages = session.exec(
        select(Messages).where(
            (Messages.sender_id == user_id) &
            (Messages.receiver_id == active.user_id) &
            (Messages.is_seen == False)
        )
    ).all()

    for msg in messages:
        msg.is_seen = True

    session.commit()

    # 🔥 Broadcast seen update
    for msg in messages:
        payload = {
            "type": "seen",
            "message_id": msg.message_id
        }
        await manager.broadcast(json.dumps(payload))

    return {"message": "Seen updated"}
