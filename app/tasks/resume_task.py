from sqlmodel import Session, select
from loguru import logger

from app.celery import app
from app.database.engine import engine
from app.database.models import Resume, ResumeStatus
from app.modules.ocr import extract_text_from_pdf
from app.modules.vectordb import vectordb_manager
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
                
                # Process CV text into vectors and store in Qdrant
                if texts and texts.strip():
                    logger.info(f"Processing CV vectors for resume {resume_id}")
                    
                    # Prepare metadata for vector storage
                    vector_metadata = {
                        "fullname": resume.fullname,
                        "email": resume.email,
                        "category": resume.category,
                        "skills": resume.skills,
                        "file_name": resume.file_name
                    }
                    
                    # Store CV vectors in Qdrant
                    vector_success = vectordb_manager.store_cv_vectors(
                        resume_id=resume_id,
                        cv_text=texts,
                        metadata=vector_metadata
                    )
                    
                    if vector_success:
                        logger.info(f"Successfully stored vectors for resume {resume_id}")
                    else:
                        logger.warning(f"Failed to store vectors for resume {resume_id}, but continuing with resume processing")
                else:
                    logger.warning(f"No text available for vector processing for resume {resume_id}")
                
                resume.status = ResumeStatus.COMPLETED

                session.add(resume)
                session.commit()

            except Exception as e:
                # Log error and mark as failed
                logger.error(f"Error processing resume {resume_id}: {e}")
                resume.status = ResumeStatus.PENDING  # Reset to pending for retry
                session.add(resume)
                session.commit()
                raise e
