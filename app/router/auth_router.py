from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from loguru import logger
from sqlmodel import Session, or_, select

from app.core.settings import settings
from app.database.engine import db_session
from app.database.models import User
from app.schema.auth import AuthRegister, RegisterResponse, Token, UserResponse
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(db_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.HASHING_SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user


@auth_router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: Request, user_data: AuthRegister, session: Session = Depends(db_session)):
    user_is_registered = session.exec(select(User).where(User.email == user_data.email)).first()
    if user_is_registered:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_username = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    hashed_password = auth_service.hash_password(user_data.password)
    user = User(email=user_data.email, password_hash=hashed_password, username=user_data.username)
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info(f"New user registered {user.username}")
    return user


@auth_router.post("/login", response_model=Token)
async def login(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(db_session)
):
    user = session.exec(
        select(User).where(or_(User.email == form_data.username, User.username == form_data.username))
    ).first()

    if not user or not auth_service.verify_password(form_data.password, user.password_hash):
        logger.warning(f"Failed login attempt from {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(payload={"sub": user.email}, expires_delta=access_token_expires)
    logger.info(f"{user.username} logged in")
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
