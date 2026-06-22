# PDF Data Extractor (AI Pipeline)

This is a microservice that extracts structured data (JSON) from raw PDF documents using FastAPI and the Google Gemini 2.5 Flash AI model.

## Architecture & Technologies
* **Framework:** FastAPI (Asynchronous, high-performance web layer)
* **AI Engine:** LangChain & Google Generative AI (Gemini)
* **File Processing:** In-memory PDF parsing for maximum speed and data security (no disk I/O).
* **Data Validation:** Pydantic for strict JSON schema enforcement and robust type checking.
* **Configuration:** `pydantic-settings` for secure, fail-fast environment variable management.

## Core Features
1. **Language-Agnostic Processing:** Capable of extracting entities, key figures, and metadata from PDFs in any language.
2. **Strict Structured Output:** Enforces strict Pydantic models to prevent AI hallucinations and ensure API reliability.
3. **Translation Pipeline:** Automatically generates a comprehensive executive summary and a list of actionable items translated into a target language, regardless of the source document's language.

## Setup and Installation

1. Create and activate a virtual environment (using uv is recommended):

    uv venv
    .venv\Scripts\activate

2. Install dependencies:

    uv pip install -r requirements.txt

3. Configure Environment Variables:
Create a .env file in the root directory of the project and add your Google Gemini API key:

    GOOGLE_API_KEY=your_google_ai_studio_api_key_here

4. Run the Application:
Start the Uvicorn server with auto-reload enabled:

    uvicorn app.main:app --reload

## Usage
Once the server is running, navigate to http://127.0.0.1:8000/docs in your browser. This will open the interactive Swagger UI where you can test the POST /api/v1/extract endpoint by uploading a PDF file directly.