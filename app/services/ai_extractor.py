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

    async def extract(self, text: str) -> ExtractionResponse:
        logger.info("Sending document text to Gemini structured LLM (length: %d chars)...", len(text))
        prompt = (
            "Please read the following document and extract the requested data. "
            "Strictly adhere to the JSON schema! For the Translation section, write the "
            "summary and action items strictly in Hungarian, regardless of the language "
            "of the original text!\n\n"
            f"Document text:\n{text}"
        )
        result = await self.structured_llm.ainvoke(prompt)
        logger.info("Structured response successfully received from Gemini.")
        return result

ai_extractor = AIExtractor()


