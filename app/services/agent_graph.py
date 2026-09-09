import logging
from typing import Optional, TypedDict
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.schemas.extraction import (
    ClassificationResult,
    DocumentMetadata,
    ResearchAnalysis,
    BusinessAnalysis,
    ExtractedData,
    TranslationPipeline,
    ExtractionResponse
)

logger = logging.getLogger(__name__)

MAX_DOCUMENT_CHARS = 15000


class AgentState(TypedDict, total=False):
    document_text: str
    target_language: str
    classification: ClassificationResult
    document_metadata: DocumentMetadata
    research_analysis: Optional[ResearchAnalysis]
    business_analysis: Optional[BusinessAnalysis]
    extracted_data: ExtractedData
    translation_pipeline: TranslationPipeline
    dispatched_agent: str


class ClassifierOutput(BaseModel):
    classification: ClassificationResult
    metadata: DocumentMetadata


class ResearchAgentOutput(BaseModel):
    research_analysis: ResearchAnalysis
    extracted_data: ExtractedData
    translation_pipeline: TranslationPipeline


class BusinessAgentOutput(BaseModel):
    business_analysis: BusinessAnalysis
    extracted_data: ExtractedData
    translation_pipeline: TranslationPipeline


class StandardExtractorOutput(BaseModel):
    extracted_data: ExtractedData
    translation_pipeline: TranslationPipeline


class DocumentAgentWorkflow:
    def __init__(self):
        logger.info("Initializing DocumentAgentWorkflow with Gemini Flash...")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("router", self._router_node)
        workflow.add_node("research_specialist", self._research_specialist_node)
        workflow.add_node("business_specialist", self._business_specialist_node)
        workflow.add_node("standard_extractor", self._standard_extractor_node)

        workflow.set_entry_point("router")

        workflow.add_conditional_edges(
            "router",
            self._route_document,
            {
                "research": "research_specialist",
                "business_proposal": "business_specialist",
                "general": "standard_extractor"
            }
        )

        workflow.add_edge("research_specialist", END)
        workflow.add_edge("business_specialist", END)
        workflow.add_edge("standard_extractor", END)

        return workflow.compile()

    async def _router_node(self, state: AgentState) -> dict:
        target_lang = state.get("target_language", "Hungarian")
        logger.info("Step 1: Router analyzing document type in %s context...", target_lang)
        text_sample = state["document_text"][:2500]

        prompt = (
            "You are an expert Document Classification and Routing Agent in an Enterprise Document Pipeline. "
            "Analyze the following document excerpt and classify it strictly into one of three categories:\n"
            "1. 'research' -> Scientific articles, academic papers, technological breakthroughs, patents, or lab reports.\n"
            "2. 'business_proposal' -> Commercial proposals, grant applications, investment pitch decks, project budgets, or business plans.\n"
            "3. 'general' -> Invoices, simple receipts, general contracts, resumes, or generic corporate memos.\n\n"
            f"TARGET LANGUAGE REQUIREMENT:\n"
            f"Write the classification 'rationale' and 'document_type' strictly in {target_lang}.\n"
            "Also infer the document title, primary language, and high-level document type.\n\n"
            f"Document Sample:\n{text_sample}"
        )

        structured_router = self.llm.with_structured_output(ClassifierOutput)
        result: ClassifierOutput = await structured_router.ainvoke(prompt)
        logger.info(
            "Router classified as '%s' (Confidence: %.2f)",
            result.classification.doc_type, result.classification.confidence
        )

        return {
            "classification": result.classification,
            "document_metadata": result.metadata
        }

    def _route_document(self, state: AgentState) -> str:
        classification = state.get("classification")
        if classification is None:
            return "general"
        doc_type = classification.doc_type
        if doc_type == "research":
            return "research"
        elif doc_type == "business_proposal":
            return "business_proposal"
        return "general"

    async def _research_specialist_node(self, state: AgentState) -> dict:
        target_lang = state.get("target_language", "Hungarian")
        logger.info("Step 2: Research Specialist evaluating TRL and synthesizing summary (target_lang: %s)...", target_lang)
        prompt = (
            "You are a Senior Technology Transfer Specialist and Academic Research Evaluator in an Enterprise Pipeline. "
            "Evaluate this scientific/technological document for commercial readiness and provide an executive synthesis.\n"
            "1. Assess the Technology Readiness Level (TRL on a scale of 1 to 9) with concrete evidence from the text.\n"
            "2. Identify the core scientific novelty or breakthrough.\n"
            "3. Suggest 2-4 concrete commercial/industrial use cases.\n"
            "4. Highlight critical development gaps or missing experimental validations before market entry.\n"
            "5. Extract key research institutions/authors and important numerical metrics (e.g. accuracy %, efficiency, sample size).\n"
            "6. In 'translation_pipeline', provide a comprehensive executive summary of the document and concrete action items.\n\n"
            f"CRITICAL TARGET LANGUAGE REQUIREMENT:\n"
            f"The user's chosen target language is '{target_lang}'.\n"
            f"ALL qualitative text MUST be written STRICTLY in {target_lang}:\n"
            f"- 'trl_justification' MUST be in {target_lang}.\n"
            f"- 'scientific_novelty' MUST be in {target_lang}.\n"
            f"- All entries in 'commercial_use_cases' MUST be in {target_lang}.\n"
            f"- All entries in 'development_gaps' MUST be in {target_lang}.\n"
            f"- 'important_numbers' metric keys MUST be in {target_lang}.\n"
            f"- 'translation_pipeline' (both 'summary' and 'action_items') MUST be written STRICTLY in {target_lang}.\n"
            f"Do NOT answer in English when {target_lang} is requested!\n\n"
            f"Document Text:\n{state['document_text'][:MAX_DOCUMENT_CHARS]}"
        )

        structured_agent = self.llm.with_structured_output(ResearchAgentOutput)
        result: ResearchAgentOutput = await structured_agent.ainvoke(prompt)

        return {
            "research_analysis": result.research_analysis,
            "extracted_data": result.extracted_data,
            "translation_pipeline": result.translation_pipeline,
            "dispatched_agent": "🔬 Research & Innovation Specialist (TRL & Tech-Transfer)"
        }

    async def _business_specialist_node(self, state: AgentState) -> dict:
        target_lang = state.get("target_language", "Hungarian")
        logger.info("Step 2: Business Proposal Specialist evaluating feasibility and synthesizing summary (target_lang: %s)...", target_lang)
        prompt = (
            "You are a Venture Capital Analyst and Enterprise Project Evaluator in an Enterprise Pipeline. "
            "Evaluate this business proposal or project plan for feasibility and risk, and provide an executive synthesis.\n"
            "1. Extract project budget, funding requested, or revenue figures.\n"
            "2. Extract expected ROI or commercial milestones.\n"
            "3. Assign an objective Feasibility Score (1-10) considering budget and timeline realism.\n"
            "4. Perform a risk assessment across financial, execution, and market risks.\n"
            "5. Provide an executive recommendation (e.g. approve, revise, reject).\n"
            "6. Extract key companies/stakeholders and important monetary/timeline numbers.\n"
            "7. In 'translation_pipeline', provide a comprehensive executive summary of the document and concrete action items.\n\n"
            f"CRITICAL TARGET LANGUAGE REQUIREMENT:\n"
            f"The user's chosen target language is '{target_lang}'.\n"
            f"ALL qualitative text MUST be written STRICTLY in {target_lang}:\n"
            f"- 'roi_forecast' MUST be in {target_lang}.\n"
            f"- 'recommendation' MUST be in {target_lang}.\n"
            f"- In 'risk_assessment', both the risk category 'key' and description 'value' MUST be in {target_lang}.\n"
            f"- 'important_numbers' metric names ('key') MUST be in {target_lang}.\n"
            f"- 'translation_pipeline' (both 'summary' and 'action_items') MUST be written STRICTLY in {target_lang}.\n"
            f"Do NOT answer in English when {target_lang} is requested!\n\n"
            f"Document Text:\n{state['document_text'][:MAX_DOCUMENT_CHARS]}"
        )

        structured_agent = self.llm.with_structured_output(BusinessAgentOutput)
        result: BusinessAgentOutput = await structured_agent.ainvoke(prompt)

        return {
            "business_analysis": result.business_analysis,
            "extracted_data": result.extracted_data,
            "translation_pipeline": result.translation_pipeline,
            "dispatched_agent": "💼 Business Proposal & Commercial Feasibility Specialist"
        }

    async def _standard_extractor_node(self, state: AgentState) -> dict:
        target_lang = state.get("target_language", "Hungarian")
        logger.info("Step 2: Standard Extractor extracting data and synthesizing summary in %s...", target_lang)
        prompt = (
            "You are a Standard Enterprise Data Extraction Pipeline. "
            "This document is a standard corporate file (e.g. invoice, receipt, general memo) that does NOT require an autonomous domain specialist agent. "
            "Perform standard baseline entity and numerical metric extraction, and provide an executive summary.\n"
            "1. Extract key entities (companies, persons, tools) and all important numbers/dates/metrics in key-value pairs.\n"
            "2. In 'translation_pipeline', provide a concise executive summary of the document and actionable takeaways if any.\n\n"
            f"CRITICAL TARGET LANGUAGE REQUIREMENT:\n"
            f"The target language is '{target_lang}'.\n"
            f"All labels/keys in 'important_numbers' MUST be written in {target_lang} (e.g. 'Összesen fizetendő', 'Számla kelte').\n"
            f"'translation_pipeline' (both 'summary' and 'action_items') MUST be written STRICTLY in {target_lang}.\n\n"
            f"Document Text:\n{state['document_text'][:MAX_DOCUMENT_CHARS]}"
        )

        structured_agent = self.llm.with_structured_output(StandardExtractorOutput)
        result: StandardExtractorOutput = await structured_agent.ainvoke(prompt)

        return {
            "extracted_data": result.extracted_data,
            "translation_pipeline": result.translation_pipeline,
            "dispatched_agent": "📄 Standard Extractor (No Specialist Agent)"
        }

    async def process_document(self, text: str, target_language: str) -> ExtractionResponse:
        initial_state: AgentState = {
            "document_text": text,
            "target_language": target_language
        }

        final_state = await self.graph.ainvoke(initial_state)

        return ExtractionResponse(
            dispatched_agent=final_state.get("dispatched_agent", "📄 Standard Extractor (No Specialist Agent)"),
            classification=final_state["classification"],
            document_metadata=final_state["document_metadata"],
            research_analysis=final_state.get("research_analysis"),
            business_analysis=final_state.get("business_analysis"),
            extracted_data=final_state.get("extracted_data", ExtractedData()),
            translation_pipeline=final_state.get("translation_pipeline", TranslationPipeline(summary="", action_items=[]))
        )


document_workflow = DocumentAgentWorkflow()
