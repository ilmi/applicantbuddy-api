from sqlmodel import Session, select

from app.celery import app
from app.database.engine import engine
from app.database.models import Resume, ResumeStatus
from app.modules.ocr import extract_text_from_pdf
from app.services.resume.resume_methods import extract_resume, summarize_resume


@app.task
def process_resume(resume_id):
    with Session(engine) as session:
        statement = select(Resume).where(Resume.id == resume_id)
        resume = session.exec(statement).first()

        if resume:
            try:
                resume.status = ResumeStatus.PROCESSING
                session.add(resume)
                session.commit()

                file_path = resume.file_path
                file_name = resume.file_name

                # Extract text from PDF using OCR
                texts = extract_text_from_pdf(file_path, file_name)

                # Generate summary
                summarized = summarize_resume(texts)

                # Extract key information
                key_information = extract_resume(texts)

                # Update resume with extracted information
                resume.fullname = key_information.get("full_name", "")
                resume.email = key_information.get("email", "")
                resume.phone = key_information.get("phone", "")
                resume.address = key_information.get("address", "")
                resume.category = key_information.get("category", "")
                resume.skills = key_information.get("skills", [])
                resume.strength = key_information.get("strength", [])
                resume.summary = summarized or ""
                resume.raw_resume = texts or ""
                resume.status = ResumeStatus.COMPLETED

                session.add(resume)
                session.commit()

            except Exception as e:
                # Log error and mark as failed
                print(f"Error processing resume {resume_id}: {e}")
                resume.status = ResumeStatus.PENDING  # Reset to pending for retry
                session.add(resume)
                session.commit()
                raise e
