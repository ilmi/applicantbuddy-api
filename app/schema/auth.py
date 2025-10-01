from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AuthRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    username: str = Field(..., min_length=3, max_length=20)


class RegisterResponse(BaseModel):
    id: str
    username: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class UserResponse(BaseModel):
    id: str
    username: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
