from fastapi import Depends
from sqlmodel import Session

from app.database.engine import db_session
from app.database.models import Resume


def create_resume(file_name:str,file_path:str,
    db: Session = Depends(db_session)):
        resume = Resume(file_name=file_name, file_path=file_path) #type: ignore
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
