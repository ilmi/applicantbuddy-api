import os
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session, desc, select

from app.database.engine import db_session
from app.database.models import Resume
from app.modules.vector import query_resume_from_vector_db
from app.services.resume.resume_methods import validate_pdf_file
from app.services.resume.resume_schema import (
    FileUploadResponse,
    QueryResumeRequest,
    ResumeResponse,
    ResumeSingleResponse,
)
from app.services.resume.resume_service import create_resume
from app.services.resume.resume_tasks import process_resume

resume_router = APIRouter(prefix="/resumes", tags=["resume"])


@resume_router.get("/", response_model=list[ResumeResponse])
async def get_resumes(
    db: Session = Depends(db_session),
):
    statement = select(Resume).order_by(desc(Resume.created_at))
    resumes = db.exec(statement).all()
    return resumes


@resume_router.get("/{resume_id}", response_model=ResumeSingleResponse)
async def get_resume(
    resume_id: str,
    db: Session = Depends(db_session),
):
    statement = select(Resume).where(Resume.id == resume_id)
    resume = db.exec(statement).first()
    return resume


@resume_router.post("/query")
async def query_resume(
    body: QueryResumeRequest,
):
    results = query_resume_from_vector_db(body.query)
    return results


@resume_router.post("/", response_model=FileUploadResponse)
async def upload_resume(
    file: Annotated[UploadFile, Depends(validate_pdf_file)],
    db: Session = Depends(db_session),
):
    contents = await file.read()
    original_filename = file.filename or "unknown_file.pdf"

    file_extension = os.path.splitext(original_filename)[1]

    resume = create_resume(
        file_name=original_filename,
        file_path="",
        db=db,
    )

    new_filename = f"{resume.id}{file_extension}"
    file_path = f"public/resumes/{new_filename}"

    resume.file_name = new_filename
    resume.file_path = file_path
    db.add(resume)
    db.commit()
    db.refresh(resume)

    os.makedirs("public/resumes", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)


    process_resume.delay(resume.id) #type: ignore
    return FileUploadResponse(
        message="Resume uploaded successfully",
        file_name=new_filename,
        file_path=file_path,
    )
