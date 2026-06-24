import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, status
from app.services.pdf_parser import extract_text
from app.services.ai_extractor import ai_extractor
from app.schemas.extraction import ExtractionResponse
from app.core.security import limiter

logger = logging.getLogger(__name__)

router=APIRouter()

MAX_FILE_SIZE=10*1024*1024
ALLOWED_MIME_TYPES = ["application/pdf"]

@router.post("/extract", response_model=ExtractionResponse)
@limiter.limit("5/minute")
async def extract_data_from_pdf(request:Request, file:UploadFile = File(...)):

    filename = file.filename or ""
    logger.info("Received extraction request for file: %s (Content-Type: %s)", filename, file.content_type)

    if file.content_type not in ALLOWED_MIME_TYPES or not filename.lower().endswith('.pdf'):
        logger.warning(
            "Rejected upload: File format not allowed. Name: %s, Content-Type: %s", 
            filename, file.content_type
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Invalid format. Only PDF files are accepted!"
        )

    if file.size is not None and file.size > MAX_FILE_SIZE:
        logger.warning("Rejected upload: File size %s exceeds MAX_FILE_SIZE", file.size)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10 MB limit."
        )

    try:
        file_bytes = bytearray()
        while chunk := await file.read(1024 * 1024):
            file_bytes.extend(chunk)
            if len(file_bytes) > MAX_FILE_SIZE:
                logger.warning("Rejected upload: Streamed size exceeds limit during read.")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File size exceeds the 10 MB limit."
                )
        
        logger.info("Extracting text from PDF...")
        text = extract_text(bytes(file_bytes))
        
        logger.info("Extracting structured metadata and translation using AI...")
        response = await ai_extractor.extract(text)
        
        logger.info("Extraction complete for file: %s", filename)
        return response
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Validation error during extraction for %s: %s", filename, str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error during PDF processing for %s: %s", filename, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")