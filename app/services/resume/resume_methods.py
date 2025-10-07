from fastapi import File, HTTPException, UploadFile

from app.services.resume.resume_schema import ExtractResume
from app.utils.llm_clients import openai_client


def validate_pdf_file(file: UploadFile = File(...)) -> UploadFile:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed. Please upload a PDF file.",
        )

    if file.filename and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed. File must have .pdf extension.",
        )

    return file


def summarize_resume(raw_text: str) -> str:
    SYSTEM_PROMPT = """
        You are a resume summarizer.
        Your task is to summarize the resume text provided.
        The summary should be concise and focus on the key information.
        The summary should be in bullet points.

        # OUTPUT FORMAT
        - Bullet point 1
        - Bullet point 2
        - Bullet point 3
        - Continue...

        # GUIDELINES
        - The summary should be in bullet points.
        - Each bullet point should direct and concise.
        - The summary should cover the following sections:
            - Personal Information
            - Education
            - Work Experience
            - Skills
            - Projects
            - Certifications
            - Interests
            - References
        """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Resume text: {raw_text}"},
        ],
    )
    summary = response.choices[0].message.content
    return summary


def extract_resume(raw_text: str):
    SYSTEM_PROMPT = """
        You are a resume information extractor.
        Your task is to extract key information from the resume text provided.

        Extract the following information:
        - Full name of the person
        - Email address
        - Phone number
        - Address
        - Category/Job role (classify as one of: software_engineer, data_scientist, product_manager, marketing_manager, sales_manager, other)
        - Skills (list of technical and professional skills)
        - Strengths (list of key strengths, maximum 5 words each)

        If any information is not available, provide empty string for strings or empty list for lists.
        Ensure all fields are properly filled according to the schema.
    """

    try:
        response = openai_client.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Resume text: {raw_text}"},
            ],
            response_format=ExtractResume,
        )

        if response.choices[0].message.parsed:
            category = response.choices[0].message.parsed
            return category.model_dump()
        else:
            # Fallback if parsing fails
            return {
                "full_name": "",
                "email": "",
                "phone": "",
                "address": "",
                "category": "other",
                "skills": [],
                "strength": [],
            }
    except Exception as e:
        # Log the error and return default values
        print(f"Error extracting resume information: {e}")
        return {
            "full_name": "",
            "email": "",
            "phone": "",
            "address": "",
            "category": "other",
            "skills": [],
            "strength": [],
        }
