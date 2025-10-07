import os

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session, desc, select

from app.database.engine import db_session
from app.database.models import Resume

resume_router = APIRouter(prefix="/resume", tags=["resume"])


@resume_router.get("/")
async def get_resume(db: Session = Depends(db_session)):
    statement = select(Resume).order_by(desc(Resume.created_at))
    resume = db.exec(statement).all()
    return resume

@resume_router.post("/")
async def upload_resume(
    file: UploadFile,
    db: Session = Depends(db_session)
):
    contents = await file.read()
    original_filename = file.filename or "tidak_diketahui.pdf"
    file_extension = os.path.splitext(original_filename)[1]

    resume = Resume(
        file_name = original_filename, file_path=f"public/resumes/{original_filename}"
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    file_path = f"public/resumes/{original_filename}"
    os.makedirs("public/resumes", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "message" : "Resume uploaded successfully"
    }
