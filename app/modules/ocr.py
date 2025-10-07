from app.utils.llm_clients import mistral_client


def extract_text_from_pdf(file_path, file_name):
    uploaded_pdf = mistral_client.files.upload(
        file={
            "file_name": file_name,
            "file_path": file_path
        },
        purpose="ocr"
    )
    signed_url = mistral_client.ocr.get_signed_url(
        file_id=uploaded_pdf.id
    )
    ocr_response = mistral_client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type":"document_url",
            "document_url": signed_url.url
        },
        include_image_base64=True
    )

    texts = ""

    for page in ocr_response.pages:
        markdown = page.markdown
        texts += markdown

    return texts


