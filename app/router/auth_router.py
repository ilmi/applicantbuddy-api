import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlmodel import Session

from app.database.engine import db_session
from app.database.models import User
from app.schema.auth import AuthRegister, RegisterResponse
from app.services import auth_service

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def is_valid_email(email: str) -> bool:
    # Simple regex for email validation
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

@auth_router.post("/register", response_model=RegisterResponse)
def register_user(user_data: AuthRegister, session: Session = Depends(db_session)):
    if not is_valid_email(user_data.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    user_is_registered = session.exec(select(User).where(User.email == user_data.email)).first()
    if user_is_registered:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_username = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    hashed_password = auth_service.hash_password(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        username = user_data.username
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
