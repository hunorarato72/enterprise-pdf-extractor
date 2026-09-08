from typing import Literal, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    title: str = Field(description="The inferred title or main topic of the document.")
    detected_language: str = Field(description="The primary language of the document (e.g., 'English', 'Hungarian', 'German').")
    document_type: str = Field(description="The general type of the document (e.g., 'Scientific Article', 'Business Proposal', 'Contract', 'General Report').")


class KeyValuePair(BaseModel):
    key: str = Field(description="The name of the metric, entity, or risk category (e.g., 'Total Budget', 'TRL Level', 'Financial Risk').")
    value: str = Field(description="The value or description itself (e.g., '150,000 EUR', 'TRL 4 - Lab Validated').")


class ExtractedData(BaseModel):
    key_entities: list[str] = Field(default_factory=list, description="List of key institutions, companies, researchers, or core technologies mentioned.")
    important_numbers: list[KeyValuePair] = Field(default_factory=list, description="Important figures, metrics, percentages, dates, or milestones.")


class ClassificationResult(BaseModel):
    doc_type: Literal["research", "business_proposal", "general"] = Field(
        description="The classified document category based on content and structure."
    )
    confidence: float = Field(
        description="Confidence score of classification between 0.0 and 1.0 (e.g. 0.95)."
    )
    rationale: str = Field(
        description="Brief explanation of why this category was chosen based on document characteristics."
    )


class ResearchAnalysis(BaseModel):
    trl_level: int = Field(
        ge=1, le=9,
        description="Estimated Technology Readiness Level (1=Basic principles observed, 4=Component validation in lab, 9=Actual system proven in operational environment)."
    )
    trl_justification: str = Field(
        description="Specific reasoning and evidence from the text supporting this TRL rating."
    )
    scientific_novelty: str = Field(
        description="The primary scientific or technological breakthrough/novelty introduced in the paper."
    )
    commercial_use_cases: list[str] = Field(
        default_factory=list,
        description="Potential industrial or commercial use cases and target markets for this innovation."
    )
    development_gaps: list[str] = Field(
        default_factory=list,
        description="Unresolved challenges, missing experimental validations, or next research milestones needed for commercialization."
    )


class BusinessAnalysis(BaseModel):
    project_budget: Optional[str] = Field(
        default="Not specified",
        description="Total budget, funding requested, or revenue figures extracted from the text."
    )
    roi_forecast: Optional[str] = Field(
        default="Not specified",
        description="Expected Return on Investment, profit margins, or commercial impact."
    )
    feasibility_score: int = Field(
        ge=1, le=10,
        description="Overall feasibility score (1=Extremely risky / unrealistic, 10=Fully validated and ready to execute)."
    )
    risk_assessment: list[KeyValuePair] = Field(
        default_factory=list,
        description="Key risks identified (e.g., Financial Risk, Execution Risk, Market Adoption Risk) with severity."
    )
    recommendation: str = Field(
        description="Strategic decision recommendation (e.g., 'Approved for Tech-Transfer Screening', 'Requires Revision of Milestones', etc.)."
    )


class TranslationPipeline(BaseModel):
    summary: str = Field(
        description="A comprehensive executive summary of the document, written strictly in the requested target language."
    )
    action_items: list[str] = Field(
        default_factory=list,
        description="A list of actionable items or recommendations extracted from the text, written strictly in the requested target language."
    )


class ExtractionResponse(BaseModel):
    dispatched_agent: str = Field(
        default="General Document Specialist",
        description="The name of the specialized AI agent that analyzed this document."
    )
    classification: ClassificationResult = Field(
        default_factory=lambda: ClassificationResult(
            doc_type="general",
            confidence=1.0,
            rationale="Standard classification"
        ),
        description="The classified document category based on content and structure."
    )
    document_metadata: DocumentMetadata
    research_analysis: Optional[ResearchAnalysis] = None
    business_analysis: Optional[BusinessAnalysis] = None
    extracted_data: ExtractedData
    translation_pipeline: TranslationPipeline