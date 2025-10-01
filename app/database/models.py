from sqlmodel import Field

from app.core.models import BaseModel
from app.utils.generate_ids import generate_id


class User(BaseModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    username: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    role: str = Field(default="user")
