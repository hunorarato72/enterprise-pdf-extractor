import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.schemas.extraction import ExtractionResponse

logger = logging.getLogger(__name__)

class AIExtractor:
    def __init__(self):
        logger.info("Initializing AIExtractor with ChatGoogleGenerativeAI (gemini-2.5-flash)...")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )
        self.structured_llm = self.llm.with_structured_output(ExtractionResponse)

    async def extract(self, text: str, target_language: str) -> ExtractionResponse:
        """
        Kinyeri a strukturált adatokat és fordítást a dokumentumból.

        target_language: A célnyelv neve angolul (pl. "German", "French", "Hungarian").
          - Az API endpointból érkezik, egyetlen query paraméterként.
          - Belefűzzük a promptba, így a Gemini tudja, milyen nyelven írja
            a 'summary' és 'action_items' mezőket.
          - Alapértelmezés: "Hungarian" (backward compatible).
        """
        logger.info(
            "Sending document text to Gemini structured LLM (length: %d chars, language: %s)...",
            len(text), target_language
        )

        prompt = (
            "Please read the following document and extract the requested data. "
            "Strictly adhere to the JSON schema!\n\n"
            f"For the 'translation_pipeline' field, write the 'summary' and 'action_items' "
            f"strictly in {target_language}, regardless of the original document's language.\n\n"
            f"Document text:\n{text}"
        )

        result = await self.structured_llm.ainvoke(prompt)
        logger.info("Structured response successfully received from Gemini.")
        return result

ai_extractor = AIExtractor()
