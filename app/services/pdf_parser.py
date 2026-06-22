import io
from pypdf import PdfReader

def extract_text(file_bytes: bytes) -> str:
    pdf_file=io.BytesIO(file_bytes)
    reader=PdfReader(pdf_file)
    
    text=""
    for page in reader.pages:
        extracted=page.extract_text()
        if extracted:
            text+= extracted + "\n"

    if not text.strip():
        raise ValueError("Could not extract text from PDF. The PDF might be encrypted or image-based.")


    return text