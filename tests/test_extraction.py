import io
import pytest
from app.schemas.extraction import ExtractionResponse, DocumentMetadata, ExtractedData, TranslationPipeline

# TEST 1: Reject invalid file formats
def test_extract_invalid_format(client):
    """
    Verify that the server correctly returns a 415 HTTP status code
    when attempting to upload a non-PDF file.
    """
    # Create in-memory file data simulating a text file
    file_data = {"file": ("test.txt", b"This is not a PDF", "text/plain")}
    
    response = client.post("/api/v1/extract", files=file_data)
    
    # Assertions: check the HTTP status code and error details
    assert response.status_code == 415
    assert "Invalid format" in response.json()["detail"]


# TEST 2: Reject files that exceed the size limit
def test_extract_file_too_large(client):
    """
    Verify that files larger than the 10 MB limit are rejected
    with a 413 HTTP status code.
    """
    # Generate an 11 MB dummy byte stream (11 * 1024 * 1024 bytes)
    large_data = b"0" * (11 * 1024 * 1024)
    file_data = {"file": ("large.pdf", large_data, "application/pdf")}
    
    response = client.post("/api/v1/extract", files=file_data)
    
    # Assertions: expect 413 Payload Too Large
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"]


# TEST 3: Mock successful data extraction and translation
def test_extract_success(client, monkeypatch):
    """
    Test the successful extraction process.
    The Gemini LLM call (ai_extractor.extract) is mocked to avoid
    calling the actual external API, returning a predefined response instead.
    """
    
    # Prepare the mocked response we expect the Gemini model to return
    expected_response = ExtractionResponse(
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

    # Define an asynchronous mock function to replace the extract method
    async def mock_extract(text: str, target_language: str):
        # Verify that the endpoint forwarded the requested target language
        assert target_language == "German"
        return expected_response

    # Mock the extract_text function to return a dummy string,
    # bypassing pypdf parsing of the invalid test bytes
    monkeypatch.setattr("app.api.endpoints.extract_text", lambda bytes_data: "Mocked PDF text content")

    # Use monkeypatch to temporarily replace the real extraction method with our mock function
    monkeypatch.setattr("app.api.endpoints.ai_extractor.extract", mock_extract)

    # Simulate a minimal PDF file payload (dummy content is now fine because pypdf is mocked)
    pdf_data = {"file": ("invoice.pdf", b"dummy pdf bytes", "application/pdf")}
    
    # Send request with target_language query parameter set to German
    response = client.post("/api/v1/extract?target_language=German", files=pdf_data)
    
    # Assertions: check status code and verify JSON contents match our expectations
    assert response.status_code == 200
    
    data = response.json()
    assert data["document_metadata"]["title"] == "Test Invoice"
    assert data["document_metadata"]["detected_language"] == "English"
    assert data["translation_pipeline"]["summary"] == "This is a mocked summary in German."


# TEST 4: Verify that the root path correctly serves the HTML interface
def test_read_root(client):
    """
    Verify that a GET request to the root path serves the HTML user interface
    with the correct content type.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "PDF Data Extractor" in response.text


# TEST 5: Verify that rate limiting blocks excessive requests
def test_rate_limit(client, monkeypatch):
    """
    Verify that sending more than 5 requests per minute triggers
    a 429 Too Many Requests HTTP status code.
    """
    # Mock the parser and AI extractor to return dummy data quickly
    monkeypatch.setattr("app.api.endpoints.extract_text", lambda bytes_data: "Dummy text")
    
    async def mock_extract(text: str, target_language: str):
        return ExtractionResponse(
            document_metadata=DocumentMetadata(title="T", detected_language="E", document_type="R"),
            extracted_data=ExtractedData(key_entities=[], important_numbers=[]),
            translation_pipeline=TranslationPipeline(summary="S", action_items=[])
        )
    monkeypatch.setattr("app.api.endpoints.ai_extractor.extract", mock_extract)

    pdf_data = {"file": ("test.pdf", b"dummy bytes", "application/pdf")}

    # Send requests in a loop until we hit the rate limit (429)
    # We use a loop of 10 to guarantee hitting the limit of 5, regardless of previous tests' requests
    rate_limited = False
    for _ in range(10):
        response = client.post("/api/v1/extract", files=pdf_data)
        if response.status_code == 429:
            rate_limited = True
            break
        assert response.status_code == 200

    # Verify that we were indeed blocked by the rate limiter eventually
    assert rate_limited is True

