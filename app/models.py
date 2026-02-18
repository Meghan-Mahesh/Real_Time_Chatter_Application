from sqlmodel import SQLModel,Field
from pydantic import EmailStr
from datetime import datetime
from typing import Optional


#----tables----
class RegisteredUsers(SQLModel, table=True):
    user_id: Optional[int] = Field(None, primary_key=True)
    user_name: str
    email: EmailStr
    pass_hash: str
    profile_pic: Optional[str] = None


class ActiveUsers(SQLModel, table=True):
    token:str=Field(...,primary_key=True)
    user_name:str=Field(...)
    login_time:datetime=Field(...)

class Messages(SQLModel, table=True):
    message_id:Optional[int]=Field(None,primary_key=True)
    user_name:str
    message:str
    timestamp:datetime

#----Pydantic Models----
class CreateUser(SQLModel):
    user_name:str
    email:EmailStr
    password:str

class LoginUser(SQLModel):
    email:EmailStr
    password:str

class ChangePasswordRequest(SQLModel):
    old_password: str
    new_password: str