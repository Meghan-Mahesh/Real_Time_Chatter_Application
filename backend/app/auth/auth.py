from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserLogin, TokenResponse
from ..utils.security import hash_password, verify_password
from .jwt import create_access_token

router = APIRouter(prefix='', tags=['Auth'])


# ===============================
# REGISTER USER / ADMIN
# ===============================
@router.post('/register', response_model=TokenResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
	import json

	existing_user = db.query(User).filter(User.username == user.username).first()
	if existing_user:
		raise HTTPException(status_code=400, detail='Username already exists')

	new_user = User(
    username=user.username,
    full_name='',
    email=user.email,
    password_hash=hash_password(user.password),
    is_admin=False
)


	db.add(new_user)
	db.commit()
	db.refresh(new_user)

	token = create_access_token({
    'user_id': new_user.id,
    'username': new_user.username,
    'is_admin': new_user.is_admin
})


	return {'access_token': token, 'token_type': 'bearer'}


# ===============================
# LOGIN USER / ADMIN
# ===============================
@router.post('/login', response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
	db_user = db.query(User).filter(User.email == user.email).first()

	if not db_user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

	if db_user.is_blocked:
		raise HTTPException(status_code=403, detail='User is blocked due to policy violation')

	if not verify_password(user.password, db_user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

	token = create_access_token({
    'user_id': db_user.id,
    'username': db_user.username,
    'is_admin': db_user.is_admin
})

	return {'access_token': token, 'token_type': 'bearer'}
