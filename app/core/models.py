from datetime import datetime

from sqlmodel import Field, SQLModel

from app.utils.generate_ids import generate_id


class BaseModel(SQLModel):
    id: str = Field(default_factory=generate_id, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)
