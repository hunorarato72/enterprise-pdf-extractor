from fastapi import APIRouter, UploadFile, File, HTTPException, Request, status
from app.services.pdf_parser import extract_text
from app.services.ai_extractor import ai_extractor
from app.schemas.extraction import ExtractionResponse
from app.core.security import limiter

router=APIRouter()

MAX_FILE_SIZE=10*1024*1024
ALLOWED_MIME_TYPES = ["application/pdf"]

@router.post("/extract", response_model=ExtractionResponse)
@limiter.limit("5/minute")
async def extract_data_from_pdf(request:Request, file:UploadFile = File(...)):

    filename = file.filename or ""
    if file.content_type not in ALLOWED_MIME_TYPES or not filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Invalid format. Only PDF files are accepted!"
        )

    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10 MB limit."
        )

    try:
        file_bytes = bytearray()
        while chunk := await file.read(1024 * 1024):
            file_bytes.extend(chunk)
            if len(file_bytes) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File size exceeds the 10 MB limit."
                )
        
        text = extract_text(bytes(file_bytes))
        response = await ai_extractor.extract(text)
        return response
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")