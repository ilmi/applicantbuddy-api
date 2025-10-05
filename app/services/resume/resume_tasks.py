from loguru import logger
from sqlmodel import Session, select

from app.celery import app
from app.database.engine import engine
from app.database.models import Resume, ResumeStatus
from app.modules.ocr import extract_text_from_pdf
from app.modules.vector import add_resume_to_vector_db
from app.services.resume.resume_methods import extract_resume, summarize_resume

# from app.utils.websocker_helper import publish_message


@app.task
def process_resume(resume_id: str):
    try:
        logger.info(f"Processing resume {resume_id}")
        # publish_message(resume_id, "Processing resume")
        with Session(engine) as session:
            statement = select(Resume).where(Resume.id == resume_id)
            resume = session.exec(statement).first()
            if resume:
                resume.status = ResumeStatus.PROCESSING
                session.add(resume)
                session.commit()

                file_path = resume.file_path
                file_name = resume.file_name

                if not file_path or not file_name:
                   raise ValueError(f"Resume {resume_id} has missing file_path or file_name")



                # publish_message(resume_id, "Extracting text from resume")
                logger.info(f"Extracting text from {file_name}")
                texts = extract_text_from_pdf(file_name, file_path)

                # publish_message(resume_id, "Extracting information from resume")
                logger.info(f"Extracting information from {file_name}")
                summarized = summarize_resume(texts)

                # publish_message(resume_id, "Extracting key information from resume")
                logger.info(f"Extracting key information from {file_name}")
                key_information = extract_resume(texts)

                resume.fullname = key_information.get("full_name")
                resume.email = key_information.get("email")
                resume.phone = key_information.get("phone")
                resume.address = key_information.get("address")
                resume.category = key_information.get("category")
                resume.skills = key_information.get("skills", [])
                resume.strength = key_information.get("strength", [])
                resume.summary = summarized
                resume.raw_resume = texts
                resume.status = ResumeStatus.COMPLETED
                session.add(resume)
                session.commit()

                # publish_message(resume_id, "Insert resume to vector db")
                logger.info(f"Insert resume to vector db {resume_id}")

                # Validate that category exists
                category = key_information.get("category")
                if not category:
                    raise ValueError(f"Resume {resume_id} extraction failed: missing category")

                add_resume_to_vector_db(
                    resume_id=resume_id,
                    category=category,
                    resume_text=texts,
                )

                # publish_message(resume_id, "completed")
                return "success"
    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {e}")
        try:
            with Session(engine) as session:
                statement = select(Resume).where(Resume.id == resume_id)
                resume = session.exec(statement).first()
                if resume:
                    resume.status = ResumeStatus.PENDING
                    session.add(resume)
                    session.commit()
        except Exception as db_error:
            logger.error(f"Failed to update resume status on error: {db_error}")
        return "error"
    finally:
        logger.info(f"Finished processing resume {resume_id}")
