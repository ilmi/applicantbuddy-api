from datetime import datetime

from pydantic import BaseModel


class AuthRegister(BaseModel):
    email: str
    password: str
    username: str

class RegisterResponse(BaseModel):
    id: str
    username: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
