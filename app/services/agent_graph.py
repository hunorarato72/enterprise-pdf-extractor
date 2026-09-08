import logging
from typing import Optional, TypedDict
from pydantic import BaseModel
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


class BusinessAgentOutput(BaseModel):
    business_analysis: BusinessAnalysis
    extracted_data: ExtractedData


class GeneralAgentOutput(BaseModel):
    extracted_data: ExtractedData


class SynthesisOutput(BaseModel):
    translation_pipeline: TranslationPipeline


class DocumentAgentWorkflow:
    def __init__(self):
        logger.info("Initializing DocumentAgentWorkflow with Gemini 2.5 Flash...")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("router", self._router_node)
        workflow.add_node("research_specialist", self._research_specialist_node)
        workflow.add_node("business_specialist", self._business_specialist_node)
        workflow.add_node("general_specialist", self._general_specialist_node)
        workflow.add_node("synthesis", self._synthesis_node)

        workflow.set_entry_point("router")

        workflow.add_conditional_edges(
            "router",
            self._route_document,
            {
                "research": "research_specialist",
                "business_proposal": "business_specialist",
                "general": "general_specialist"
            }
        )

        workflow.add_edge("research_specialist", "synthesis")
        workflow.add_edge("business_specialist", "synthesis")
        workflow.add_edge("general_specialist", "synthesis")
        workflow.add_edge("synthesis", END)

        return workflow.compile()

    async def _router_node(self, state: AgentState) -> dict:
        logger.info("Step 1: Router Agent analyzing document type and metadata...")
        text_sample = state["document_text"][:4000]

        prompt = (
            "You are an expert Document Classification and Routing Agent in an Enterprise AI Pipeline. "
            "Analyze the following document excerpt and classify it strictly into one of three categories:\n"
            "1. 'research' -> Scientific articles, academic papers, technological breakthroughs, patents, or lab reports.\n"
            "2. 'business_proposal' -> Commercial proposals, grant applications, investment pitch decks, project budgets, or business plans.\n"
            "3. 'general' -> Invoices, simple receipts, general contracts, resumes, or generic corporate memos.\n\n"
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
        doc_type = state.get("classification", {}).doc_type
        if doc_type == "research":
            return "research"
        elif doc_type == "business_proposal":
            return "business_proposal"
        return "general"

    async def _research_specialist_node(self, state: AgentState) -> dict:
        logger.info("Step 2: Research & Innovation Specialist evaluating TRL and Tech-Transfer potential...")
        prompt = (
            "You are a Senior Technology Transfer Specialist and Academic Research Evaluator. "
            "Evaluate this scientific/technological document for commercial readiness.\n"
            "1. Assess the Technology Readiness Level (TRL on a scale of 1 to 9) with concrete evidence from the text.\n"
            "2. Identify the core scientific novelty or breakthrough.\n"
            "3. Suggest 2-4 concrete commercial/industrial use cases.\n"
            "4. Highlight critical development gaps or missing experimental validations before market entry.\n"
            "5. Extract key research institutions/authors and important numerical metrics (e.g. accuracy %, efficiency, sample size).\n\n"
            f"Document Text:\n{state['document_text']}"
        )

        structured_agent = self.llm.with_structured_output(ResearchAgentOutput)
        result: ResearchAgentOutput = await structured_agent.ainvoke(prompt)

        return {
            "research_analysis": result.research_analysis,
            "extracted_data": result.extracted_data,
            "dispatched_agent": "🔬 Research & Innovation Specialist (TRL & Tech-Transfer)"
        }

    async def _business_specialist_node(self, state: AgentState) -> dict:
        logger.info("Step 2: Business Proposal Specialist evaluating feasibility and risk matrix...")
        prompt = (
            "You are a Venture Capital Analyst and Enterprise Project Evaluator. "
            "Evaluate this business proposal or project plan for feasibility and risk.\n"
            "1. Extract project budget, funding requested, or revenue figures.\n"
            "2. Extract expected ROI or commercial milestones.\n"
            "3. Assign an objective Feasibility Score (1-10) considering budget and timeline realism.\n"
            "4. Perform a risk assessment across financial, execution, and market risks.\n"
            "5. Provide an executive recommendation (e.g. approve, revise, reject).\n"
            "6. Extract key companies/stakeholders and important monetary/timeline numbers.\n\n"
            f"Document Text:\n{state['document_text']}"
        )

        structured_agent = self.llm.with_structured_output(BusinessAgentOutput)
        result: BusinessAgentOutput = await structured_agent.ainvoke(prompt)

        return {
            "business_analysis": result.business_analysis,
            "extracted_data": result.extracted_data,
            "dispatched_agent": "💼 Business Proposal & Commercial Feasibility Specialist"
        }

    async def _general_specialist_node(self, state: AgentState) -> dict:
        logger.info("Step 2: General Specialist extracting entities and numerical data...")
        prompt = (
            "You are an Enterprise Data Extraction Specialist. "
            "Extract key entities (companies, persons, tools) and all important numbers/dates/metrics in key-value pairs.\n\n"
            f"Document Text:\n{state['document_text']}"
        )

        structured_agent = self.llm.with_structured_output(GeneralAgentOutput)
        result: GeneralAgentOutput = await structured_agent.ainvoke(prompt)

        return {
            "extracted_data": result.extracted_data,
            "dispatched_agent": "📄 General Enterprise Document Specialist"
        }

    async def _synthesis_node(self, state: AgentState) -> dict:
        target_lang = state.get("target_language", "Hungarian")
        agent_name = state.get("dispatched_agent", "Specialist")
        logger.info("Step 3: Synthesis Node formulating executive summary in %s...", target_lang)

        context_details = []
        if state.get("research_analysis"):
            ra = state["research_analysis"]
            context_details.append(f"TRL Level: {ra.trl_level} - {ra.trl_justification}")
            context_details.append(f"Novelty: {ra.scientific_novelty}")
        elif state.get("business_analysis"):
            ba = state["business_analysis"]
            context_details.append(f"Budget: {ba.project_budget}, Feasibility Score: {ba.feasibility_score}/10")
            context_details.append(f"Recommendation: {ba.recommendation}")

        prompt = (
            f"You are the Lead Executive Communicator in an AI Workflow. "
            f"Synthesize the findings from {agent_name} into an executive brief. "
            f"Crucially, the 'summary' and 'action_items' MUST be written STRICTLY in {target_lang}.\n\n"
            f"Specialist findings:\n" + "\n".join(context_details) + "\n\n"
            f"Full Document context:\n{state['document_text'][:3000]}"
        )

        structured_synthesis = self.llm.with_structured_output(SynthesisOutput)
        result: SynthesisOutput = await structured_synthesis.ainvoke(prompt)

        return {
            "translation_pipeline": result.translation_pipeline
        }

    async def process_document(self, text: str, target_language: str) -> ExtractionResponse:
        initial_state: AgentState = {
            "document_text": text,
            "target_language": target_language
        }

        final_state = await self.graph.ainvoke(initial_state)

        return ExtractionResponse(
            dispatched_agent=final_state.get("dispatched_agent", "General Document Specialist"),
            classification=final_state["classification"],
            document_metadata=final_state["document_metadata"],
            research_analysis=final_state.get("research_analysis"),
            business_analysis=final_state.get("business_analysis"),
            extracted_data=final_state.get("extracted_data", ExtractedData()),
            translation_pipeline=final_state.get("translation_pipeline", TranslationPipeline(summary="", action_items=[]))
        )


document_workflow = DocumentAgentWorkflow()
