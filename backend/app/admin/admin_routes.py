from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io

from ..database import get_db
from ..models import User, Message
from ..auth.jwt import get_current_admin
from ..utils.security import hash_password


router = APIRouter(tags=["Admin"])


# ===============================
# GET ALL USERS
# ===============================
@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    users = db.query(User).all()
    return users


# ===============================
# GET BLOCKED USERS
# ===============================
@router.get("/blocked-users")
def blocked_users(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    users = db.query(User).filter(User.is_blocked == True).all()
    return users


# ===============================
# GET ALL MESSAGES
# ===============================
@router.get("/messages")
def get_all_messages(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    messages = db.query(Message).all()
    return messages


# ===============================
# DOWNLOAD USERS CSV
# ===============================
@router.get("/download/users")
def download_users_csv(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["id", "username", "full_name", "is_admin", "is_blocked", "created_at"])

    users = db.query(User).all()
    for u in users:
        writer.writerow([
            u.id,
            u.username,
            u.full_name,
            u.is_admin,
            u.is_blocked,
            u.created_at
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )


# ===============================
# DOWNLOAD MESSAGES CSV
# ===============================
@router.get("/download/messages")
def download_messages_csv(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "id",
        "sender_username",
        "receiver_username",
        "room",
        "content",
        "timestamp"
    ])

    messages = db.query(Message).all()
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        receiver = db.query(User).filter(User.id == m.receiver_id).first() if m.receiver_id else None
        writer.writerow([
            m.id,
            sender.username if sender else "Unknown",
            receiver.username if receiver else "",
            m.room,
            m.content,
            m.timestamp
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=messages.csv"}
    )

# ===============================
# ADMIN DASHBOARD SUMMARY
# ===============================
@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    total_messages = db.query(Message).count()
    blocked_users = db.query(User).filter(User.is_blocked == True).count()

    recent_messages = (
        db.query(Message)
        .order_by(Message.id.desc())
        .limit(10)
        .all()
    )

    formatted_messages = []
    for m in recent_messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        formatted_messages.append({
            "username": sender.username if sender else "Unknown",
            "message": m.content,
            "time": m.timestamp,
            "blocked": sender.is_blocked if sender else False
        })

    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "blocked_users": blocked_users,
        "messages": formatted_messages
    }

from ..utils.security import verify_password
from ..auth.jwt import create_access_token

@router.post("/login")
def admin_login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not an admin")

    token = create_access_token({
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    })

    return {"access_token": token, "token_type": "bearer"}

# ===============================
# CREATE DEFAULT ADMIN (RUN ONCE)
# ===============================
@router.get("/create-default-admin")
def create_default_admin(db: Session = Depends(get_db)):
    existing_admin = db.query(User).filter(User.email == "admin@chat.com").first()

    if existing_admin:
        return {"message": "Admin already exists"}

    admin = User(
        username="admin",
        full_name="System Admin",
        email="admin@chat.com",
        password_hash=hash_password("admin123"),
        is_admin=True
    )

    db.add(admin)
    db.commit()

    return {"message": "Default admin created successfully"}
