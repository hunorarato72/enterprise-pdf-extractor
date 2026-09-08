import logging
from app.services.agent_graph import document_workflow
from app.schemas.extraction import ExtractionResponse

logger = logging.getLogger(__name__)


class AIExtractor:
    def __init__(self):
        logger.info("Initializing AIExtractor with LangGraph Multi-Agent Workflow...")
        self.workflow = document_workflow

    async def extract(self, text: str, target_language: str) -> ExtractionResponse:
        logger.info(
            "Delegating extraction to LangGraph Multi-Agent Pipeline (text length: %d chars, target_language: %s)...",
            len(text), target_language
        )
        return await self.workflow.process_document(text, target_language=target_language)


ai_extractor = AIExtractor()
