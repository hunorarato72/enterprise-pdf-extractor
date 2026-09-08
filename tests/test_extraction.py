import pytest
from app.schemas.extraction import (
    ExtractionResponse,
    DocumentMetadata,
    ExtractedData,
    TranslationPipeline,
    ClassificationResult,
    ResearchAnalysis,
    BusinessAnalysis,
    KeyValuePair
)

# TEST 1: Reject invalid file formats
def test_extract_invalid_format(client):
    file_data = {"file": ("test.txt", b"This is not a PDF", "text/plain")}
    response = client.post("/api/v1/extract", files=file_data)
    assert response.status_code == 415
    assert "Invalid format" in response.json()["detail"]


# TEST 2: Reject files that exceed the size limit
def test_extract_file_too_large(client):
    large_data = b"0" * (11 * 1024 * 1024)
    file_data = {"file": ("large.pdf", large_data, "application/pdf")}
    response = client.post("/api/v1/extract", files=file_data)
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"]


# TEST 3: Mock successful data extraction and translation (General Specialist)
def test_extract_success(client, monkeypatch):
    expected_response = ExtractionResponse(
        dispatched_agent="📄 General Enterprise Document Specialist",
        classification=ClassificationResult(
            doc_type="general",
            confidence=0.98,
            rationale="Invoice format detected."
        ),
        document_metadata=DocumentMetadata(
            title="Test Invoice",
            detected_language="English",
            document_type="Financial Report"
        ),
        extracted_data=ExtractedData(
            key_entities=["Acme Corp"],
            important_numbers=[]
        ),
        translation_pipeline=TranslationPipeline(
            summary="This is a mocked summary in German.",
            action_items=["Action Item 1"]
        )
    )

    async def mock_extract(text: str, target_language: str):
        assert target_language == "German"
        return expected_response

    monkeypatch.setattr("app.api.endpoints.extract_text", lambda bytes_data: "Mocked PDF text content")
    monkeypatch.setattr("app.api.endpoints.ai_extractor.extract", mock_extract)

    pdf_data = {"file": ("invoice.pdf", b"dummy pdf bytes", "application/pdf")}
    response = client.post("/api/v1/extract?target_language=German", files=pdf_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["dispatched_agent"] == "📄 General Enterprise Document Specialist"
    assert data["classification"]["doc_type"] == "general"
    assert data["document_metadata"]["title"] == "Test Invoice"
    assert data["translation_pipeline"]["summary"] == "This is a mocked summary in German."


# TEST 4: Mock Research & Innovation Specialist (TRL Evaluation)
def test_extract_research_specialist(client, monkeypatch):
    expected_response = ExtractionResponse(
        dispatched_agent="🔬 Research & Innovation Specialist (TRL & Tech-Transfer)",
        classification=ClassificationResult(
            doc_type="research",
            confidence=0.96,
            rationale="Academic methodology and lab validation identified."
        ),
        document_metadata=DocumentMetadata(
            title="Perovskite Solar Cells Breakthrough",
            detected_language="English",
            document_type="Scientific Research Paper"
        ),
        research_analysis=ResearchAnalysis(
            trl_level=4,
            trl_justification="Small scale lab prototypes demonstrated 24% photon efficiency.",
            scientific_novelty="Novel double-cation passivation layer.",
            commercial_use_cases=["Building-integrated photovoltaics (BIPV)", "Aerospace solar arrays"],
            development_gaps=["Long-term thermal stability test under 85°C"]
        ),
        extracted_data=ExtractedData(
            key_entities=["National Energy Research Institute", "Advanced Materials Lab"],
            important_numbers=[KeyValuePair(key="Efficiency", value="24.2%")]
        ),
        translation_pipeline=TranslationPipeline(
            summary="Úttörő perovskite napelem kutatás.",
            action_items=["Szabadalmi bejelentés előkészítése"]
        )
    )

    async def mock_extract(text: str, target_language: str):
        return expected_response

    monkeypatch.setattr("app.api.endpoints.extract_text", lambda bytes_data: "Perovskite research text")
    monkeypatch.setattr("app.api.endpoints.ai_extractor.extract", mock_extract)

    pdf_data = {"file": ("research_paper.pdf", b"dummy bytes", "application/pdf")}
    response = client.post("/api/v1/extract?target_language=Hungarian", files=pdf_data)

    assert response.status_code == 200
    data = response.json()
    assert data["classification"]["doc_type"] == "research"
    assert data["research_analysis"]["trl_level"] == 4
    assert "Building-integrated photovoltaics (BIPV)" in data["research_analysis"]["commercial_use_cases"]


# TEST 5: Mock Business Proposal Specialist (Feasibility & Risk Matrix)
def test_extract_business_proposal(client, monkeypatch):
    expected_response = ExtractionResponse(
        dispatched_agent="💼 Business Proposal & Commercial Feasibility Specialist",
        classification=ClassificationResult(
            doc_type="business_proposal",
            confidence=0.92,
            rationale="Contains commercial milestones and budget request."
        ),
        document_metadata=DocumentMetadata(
            title="Smart Grid Expansion Grant",
            detected_language="English",
            document_type="Grant Application"
        ),
        business_analysis=BusinessAnalysis(
            project_budget="250,000 EUR",
            roi_forecast="Estimated 3.5x ROI in 36 months",
            feasibility_score=8,
            risk_assessment=[
                KeyValuePair(key="Financial Risk", value="Low - 50% co-financing secured"),
                KeyValuePair(key="Execution Risk", value="Medium - Tight regulatory approvals")
            ],
            recommendation="Approved for Tech-Transfer Screening"
        ),
        extracted_data=ExtractedData(key_entities=["TechCo Ltd."], important_numbers=[]),
        translation_pipeline=TranslationPipeline(summary="Üzleti terv.", action_items=["Támogatás jóváhagyása"])
    )

    async def mock_extract(text: str, target_language: str):
        return expected_response

    monkeypatch.setattr("app.api.endpoints.extract_text", lambda bytes_data: "Grant proposal text")
    monkeypatch.setattr("app.api.endpoints.ai_extractor.extract", mock_extract)

    pdf_data = {"file": ("proposal.pdf", b"dummy bytes", "application/pdf")}
    response = client.post("/api/v1/extract?target_language=Hungarian", files=pdf_data)

    assert response.status_code == 200
    data = response.json()
    assert data["classification"]["doc_type"] == "business_proposal"
    assert data["business_analysis"]["feasibility_score"] == 8
    assert data["business_analysis"]["project_budget"] == "250,000 EUR"


# TEST 6: Verify root serves UI
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "PDF Data Extractor" in response.text


# TEST 7: Verify rate limiting
def test_rate_limit(client, monkeypatch):
    monkeypatch.setattr("app.api.endpoints.extract_text", lambda bytes_data: "Dummy text")
    
    async def mock_extract(text: str, target_language: str):
        return ExtractionResponse(
            classification=ClassificationResult(doc_type="general", confidence=1.0, rationale="Mock"),
            document_metadata=DocumentMetadata(title="T", detected_language="E", document_type="R"),
            extracted_data=ExtractedData(key_entities=[], important_numbers=[]),
            translation_pipeline=TranslationPipeline(summary="S", action_items=[])
        )
    monkeypatch.setattr("app.api.endpoints.ai_extractor.extract", mock_extract)

    pdf_data = {"file": ("test.pdf", b"dummy bytes", "application/pdf")}

    rate_limited = False
    for _ in range(10):
        response = client.post("/api/v1/extract", files=pdf_data)
        if response.status_code == 429:
            rate_limited = True
            break
        assert response.status_code == 200

    assert rate_limited is True
