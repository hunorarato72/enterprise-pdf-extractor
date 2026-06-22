from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_parser import extract_text
from app.services.ai_extractor import ai_extractor
from app.schemas.extraction import ExtractionResponse

router=APIRouter()

@router.post("/extract", response_model=ExtractionResponse)
async def extract_data_from_pdf(file:UploadFile = File(...)):
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