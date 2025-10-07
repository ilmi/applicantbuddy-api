from pydantic import BaseModel, Field


class ExtractResume(BaseModel):
    full_name: str = Field(description="Full name of the person")
    email: str = Field(description="Email of the person")
    phone: str = Field(description="Phone number of the person")
    address: str = Field(description="Address of the person")
    category: str = Field(description="Category of the resume")
    skills: list[str] = Field(description="Skills of the person, short and direct")
    strength: list[str] = Field(
        description="Strength of the person, direct and concise, maximum 5 words each"
    )
    weakness: list[str] = Field(
        description=(
            "Weakness of the person, direct and concise, maximum 5 words each"
            "If the person has no weakness, return empty list"
        )
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
