from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from app.websocket_manager import ConnectionManager
from typing import Annotated
from app.models import RegisteredUsers, ActiveUsers, Messages, CreateUser, LoginUser, ChangePasswordRequest
from app.auth import hash_password, verify_password
from app.database import create_tables_database,BASE_DIR,get_session
from uuid import uuid4
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import UploadFile, File
import os


UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_tables_database()
    yield
SessionDep=Annotated[Session,Depends(get_session)]

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

manager = ConnectionManager()

@app.get("/")
def serve_login():
    return FileResponse("app/static/login.html")


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, session:SessionDep):

    active_user = session.get(ActiveUsers, token)

    if not active_user:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, token)

    try:
        history = session.exec(select(Messages).order_by(Messages.timestamp)).all()

        for msg in history:
            await websocket.send_text(f"[{msg.timestamp}] {msg.user_name}: {msg.message}")

        while True:
            message = await websocket.receive_text()

            # Save message to DB
            chat = Messages(
                user_name=active_user.user_name,
                message=message,
                timestamp=datetime.now()
            )
            session.add(chat)
            session.commit()

            # ✅ extract values while session is alive
            username = chat.user_name
            msg_text = chat.message
            ts = chat.timestamp


            # 🔹 Broadcast message
            await manager.broadcast(
                f"[{ts}] {username}: {msg_text}"
            )


    except WebSocketDisconnect:
        await manager.disconnect(websocket)

        session.delete(active_user)
        session.commit()


@app.post("/register")
async def register(session:SessionDep, user:CreateUser):
    if session.exec(select(RegisteredUsers).where(RegisteredUsers.email == user.email)).first():
        raise HTTPException(status_code=400,detail="User Already exist")
    hashed = hash_password(user.password)
    new_user = RegisteredUsers(email=user.email, user_name=user.user_name, pass_hash=hashed)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message":"User registered successfully"}

@app.post("/login")
async def login(session:SessionDep, user:LoginUser):
    existing_user = session.exec(select(RegisteredUsers).where(RegisteredUsers.email == user.email)).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="User doesnot exist")
    pwd = verify_password(user.password,existing_user.pass_hash)
    if not pwd:
        raise HTTPException(status_code=400,detail="Password Incorrect")

    # Generate token
    token = str(uuid4())

    # Store active user
    active = ActiveUsers(
        token=token,
        user_name=existing_user.user_name,
        login_time=datetime.now()
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


@app.post("/upload-profile-pic/{token}")
async def upload_profile_pic(session:SessionDep, token: str, file: UploadFile = File(...)):
    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(
        select(RegisteredUsers).where(
            RegisteredUsers.user_name == active.user_name
        )
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    filename = f"{user.user_id}.jpg"
    upload_dir = os.path.join(BASE_DIR, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Save path
    profile_pic_path = f"/static/uploads/{filename}"
    user.profile_pic = profile_pic_path

    session.commit()   # commit changes

    # ✅ SAFE: return stored value, not ORM object
    return {"profile_pic": profile_pic_path}
    
@app.get("/profile-pic/{token}")
def get_profile_pic(token: str, session: SessionDep):
    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401)

    user = session.exec(
        select(RegisteredUsers)
        .where(RegisteredUsers.user_name == active.user_name)
    ).first()

    return {"profile_pic": user.profile_pic}


@app.post("/change-password/{token}")
def change_password(token: str, data: ChangePasswordRequest, session:SessionDep):
    active = session.get(ActiveUsers, token)
    if not active:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(
        select(RegisteredUsers).where(
            RegisteredUsers.user_name == active.user_name
        )
    ).first()

    if not verify_password(data.old_password, user.pass_hash):
        raise HTTPException(status_code=400, detail="Old password incorrect")

    user.pass_hash = hash_password(data.new_password)
    session.commit()

    return {"message": "Password changed successfully"}

@app.get("/messages")
def get_messages(session: SessionDep):
    chats = session.exec(select(Messages).order_by(Messages.timestamp)).all()

    return [
        {
            "user_name": chat.user_name,
            "message": chat.message,
            "timestamp": chat.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for chat in chats
    ]
