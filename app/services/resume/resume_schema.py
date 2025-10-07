from pydantic import BaseModel, Field


class ExtractResume(BaseModel):
    full_name: str = Field(description="Full name of the person", default="")
    email: str = Field(description="Email of the person", default="")
    phone: str = Field(description="Phone number of the person", default="")
    address: str = Field(description="Address of the person", default="")
    category: str = Field(description="Category of the resume", default="")
    skills: list[str] = Field(description="Skills of the person, short and direct", default_factory=list)
    strength: list[str] = Field(
        description="Strength of the person, direct and concise, maximum 5 words each", default_factory=list
    )


class FileUploadResponse(BaseModel):
    message: str
    file_name: str
    file_path: str


class QueryResumeRequest(BaseModel):
    query: str


class ResumeResponse(BaseModel):
    id: str
    fullname: str
    email: str
    phone: str
    address: str
    category: str
    skills: list[str]
    status: str
    file_path: str


class ResumeSingleResponse(ResumeResponse):
    strength: list[str]
    summary: str
