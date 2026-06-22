from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    title: str = Field(description="The inferred title or main topic of the document.")
    detected_language: str = Field(description="The primary language of the document (e.g., 'English', 'Hungarian', 'German').")
    document_type: str = Field(description="The type of the document (e.g., 'Contract', 'Financial Report', 'Resume', 'Article').")

class KeyValuePair(BaseModel):
    key: str = Field(description="The name of the number or data (e.g., 'Total Amount', 'Deadline').")
    value: str = Field(description="The value itself (e.g., '1500 EUR', '2023-12-31').")

class ExtractedData(BaseModel):
    key_entities: list[str] = Field(description="List of the most important companies, individuals, or technologies mentioned in the document.")
    important_numbers: list[KeyValuePair] = Field(description="Important figures, dates, or metrics in key-value pairs (e.g., {'revenue': '15%', 'deadline': '2024-12-31'}).")

class TranslationPipeline(BaseModel):
    hungarian_summary: str = Field(description="A comprehensive executive summary of the document, written strictly in Hungarian, regardless of the original text's language.")
    hungarian_action_items: list[str] = Field(description="A list of actionable items or recommendations extracted from the text, written strictly in Hungarian.")
    
class ExtractionResponse(BaseModel):
    document_metadata: DocumentMetadata
    extracted_data: ExtractedData
    translation_pipeline: TranslationPipeline   