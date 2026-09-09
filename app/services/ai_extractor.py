from typing import Optional
import logging
from app.services.agent_graph import document_workflow
from app.schemas.extraction import ExtractionResponse

logger = logging.getLogger(__name__)


class AIExtractor:
    def __init__(self):
        logger.info("Initializing AIExtractor with LangGraph Workflow...")
        self.workflow = document_workflow

    async def extract(self, text: str, target_language: str, filename: Optional[str] = None) -> ExtractionResponse:
        logger.info(
            "Delegating extraction to LangGraph Pipeline (filename: %s, text length: %d chars, target_language: %s)...",
            filename, len(text), target_language
        )
        return await self.workflow.process_document(text, target_language=target_language, filename=filename)


ai_extractor = AIExtractor()
