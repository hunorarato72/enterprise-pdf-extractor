from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.schemas.extraction import ExtractionResponse

class AIExtractor:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.1
        )

        self.structured_llm = self.llm.with_structured_output(ExtractionResponse)

    async def extract(self, text: str) -> ExtractionResponse:
        prompt = (
            "Please read the following document and extract the requested data. "
            "Strictly adhere to the JSON schema! For the Translation section, write the "
            "summary and action items strictly in Hungarian, regardless of the language "
            "of the original text!\n\n"
            f"Document text:\n{text}"
        )
        return await self.structured_llm.ainvoke(prompt)

ai_extractor = AIExtractor()


