from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import datetime
from typing import Optional


class RegisteredUsers(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    email: EmailStr = Field(index=True, unique=True)
    pass_hash: str
    profile_pic: Optional[str] = None


class ActiveUsers(SQLModel, table=True):
    token: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="registeredusers.user_id")
    login_time: datetime = Field(default_factory=datetime.utcnow)


class Messages(SQLModel, table=True):
    message_id: Optional[int] = Field(default=None, primary_key=True)

    sender_id: int = Field(foreign_key="registeredusers.user_id")
    receiver_id: Optional[int] = Field(default=None, foreign_key="registeredusers.user_id")

    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    is_deleted: bool = False
    is_edited: bool = False
    edited_at: Optional[datetime] = None

    # 🔥 NEW FIELDS
    is_delivered: bool = False
    is_seen: bool = False



class CreateUser(SQLModel):
    user_name: str
    email: EmailStr
    password: str


class LoginUser(SQLModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(SQLModel):
    old_password: str
    new_password: str
