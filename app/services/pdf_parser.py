import io
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def extract_text(file_bytes: bytes) -> str:
    logger.info("Initializing PDF Reader to parse file bytes...")
    pdf_file=io.BytesIO(file_bytes)
    reader=PdfReader(pdf_file)
    
    num_pages = len(reader.pages)
    logger.info("PDF has %d pages. Starting text extraction...", num_pages)
    
    text=""
    for i, page in enumerate(reader.pages):
        extracted=page.extract_text()
        if extracted:
            text+= extracted + "\n"
        else:
            logger.debug("No text extracted from page %d", i + 1)

    if not text.strip():
        raise ValueError("Could not extract text from PDF. The PDF might be encrypted or image-based.")

    logger.info("Successfully extracted %d characters of text from PDF", len(text))
    return text