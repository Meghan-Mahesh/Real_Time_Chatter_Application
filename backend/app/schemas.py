from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import EmailStr
from pydantic import Field



# ===============================
# USER SCHEMAS
# ===============================
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)



class UserLogin(BaseModel):
	email: EmailStr
	password: str = Field(min_length=8)


class UserResponse(BaseModel):
	id: int
	username: str
	full_name: str
	is_admin: bool
	is_blocked: bool
	warning_count: int
	created_at: datetime
	class Config:
		from_attributes = True


# ===============================
# TOKEN SCHEMA
# ===============================
class TokenResponse(BaseModel):
	access_token: str
	token_type: str


# ===============================
# MESSAGE SCHEMA
# ===============================
class MessageResponse(BaseModel):
	id: int
	sender_id: int
	receiver_id: Optional[int]
	room: Optional[str]
	content: str
	timestamp: datetime

	class Config:
		from_attributes = True
