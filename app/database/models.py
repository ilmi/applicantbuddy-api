from typing import Optional

from sqlmodel import Field

from app.core.models import BaseModel


class ExampleModel(BaseModel, table=True):
    name: str = Field(default="Example Model")
    description: Optional[str] = None
