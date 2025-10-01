from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(payload: dict, expires_delta: timedelta = timedelta(minutes=settings.JWT_TOKEN_EXPIRED)):
    to_encode = payload.copy()
    expired_time = datetime.now() + expires_delta
    to_encode.update({"exp": expired_time})
    encoded_jwt = jwt.encode(to_encode, settings.HASHING_SECRET_KEY, algorithm=settings.HASHING_ALGORITHM)
    return encoded_jwt
