import base64
import os

from app.utils.llm_clients import mistral_client


def extract_text_from_pdf(file_path, file_name):
    """
    Extract text from PDF using Mistral OCR service.

    Args:
        file_path (str): Path to the PDF file
        file_name (str): Name of the PDF file

    Returns:
        str: Extracted text from the PDF

    Raises:
        Exception: If OCR processing fails
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Method 1: Try direct OCR processing with base64 encoding using data URI format
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
                base64_pdf = base64.b64encode(pdf_content).decode("utf-8")

            # Process OCR directly with base64 content using data URI format
            ocr_response = mistral_client.ocr.process(
                model="mistral-ocr-latest",
                document={"type": "document_url", "document_url": f"data:application/pdf;base64,{base64_pdf}"},
                include_image_base64=True,
            )

        except Exception as direct_ocr_error:
            print(f"Direct OCR failed, trying file upload method: {direct_ocr_error}")

            # Method 2: Upload file first, then process OCR
            with open(file_path, "rb") as pdf_file:
                uploaded_pdf = mistral_client.files.upload(
                    file={"file_name": file_name, "content": pdf_file}, purpose="ocr"
                )

            # Get signed URL for the uploaded file using correct method
            signed_url = mistral_client.files.get_signed_url(file_id=uploaded_pdf.id)

            # Process OCR
            ocr_response = mistral_client.ocr.process(
                model="mistral-ocr-latest",
                document={"type": "document_url", "document_url": signed_url.url},
                include_image_base64=True,
            )

        # Extract text from all pages
        texts = ""
        if hasattr(ocr_response, "pages") and ocr_response.pages:
            for page in ocr_response.pages:
                if hasattr(page, "markdown") and page.markdown:
                    texts += page.markdown + "\n"
                elif hasattr(page, "text") and page.text:
                    texts += page.text + "\n"

        if not texts.strip():
            print(f"Warning: No text extracted from {file_name}")
            return ""

        return texts.strip()

    except FileNotFoundError as e:
        print(f"File not found error for {file_name}: {e}")
        raise Exception(f"File not found: {str(e)}")
    except Exception as e:
        print(f"Error in OCR processing for file {file_name}: {e}")
        raise Exception(f"OCR processing failed: {str(e)}")
