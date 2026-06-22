from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.services.pdf_parser import extract_text
from app.services.ai_extractor import ai_extractor
from app.schemas.extraction import ExtractionResponse
from app.core.security import limiter

router=APIRouter()

@router.post("/extract", response_model=ExtractionResponse)
@limiter.limit("5/minute")
async def extract_data_from_pdf(request:Request, file:UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid format. Only PDF files are accepted!")
    
    try:
        file_bytes = await file.read()
        text = extract_text(file_bytes)
        response = await ai_extractor.extract(text)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")