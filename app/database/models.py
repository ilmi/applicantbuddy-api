from enum import Enum
from typing import List, Optional

from sqlmodel import JSON, Column, Field

from app.core.models import BaseModel


class ResumeStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"


class Resume(BaseModel, table=True):
    fullname: Optional[str] = Field("")
    email: Optional[str] = Field("")
    phone: Optional[str] = Field("")
    address: Optional[str] = Field("")
    category: Optional[str] = Field("")
    summary: Optional[str] = Field("")
    raw_resume: Optional[str] = Field("")
    file_name: Optional[str] = Field("")
    file_path: Optional[str] = Field("")
    skills: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    strength: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))

    status: ResumeStatus = Field(default=ResumeStatus.PENDING)
