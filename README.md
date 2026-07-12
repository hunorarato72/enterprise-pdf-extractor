# Enterprise PDF Data Extractor (AI Pipeline)

An asynchronous microservice built with **FastAPI** and **Docker** that extracts structured JSON data from PDF documents using the **Google Gemini 2.5 Flash** LLM, complete with an interactive web UI.

## Live Demo

The application is fully dockerized and deployed on the **DigitalOcean App Platform**. You can interact with the live web interface or view the auto-generated documentation via Swagger UI:
*   **[LIVE WEB UI & DEMO](https://enterprise-data-extractor-j6jzn.ondigitalocean.app/)**
*   **[LIVE SWAGGER UI DOCS](https://enterprise-data-extractor-j6jzn.ondigitalocean.app/docs)**

*(Note: The endpoints are secured with an IP-based rate limiter allowing a maximum of 5 requests per minute).*

## Tech Stack & Architecture

- **Backend Framework:** FastAPI (Python 3.11, fully asynchronous execution)
- **AI Engine:** Google GenAI SDK / LangChain (Gemini 2.5 Flash)
- **Frontend UI:** Vanilla HTML5, CSS3 (minimalist dark design), Javascript (drag-and-drop upload, Fetch API, and one-click JSON download)
- **Containerization:** Docker (lightweight python:3.11-slim base image)
- **Security & Rate Limiting:** slowapi (In-memory rate limiting using the limits engine)
- **Data Validation:** Pydantic (Strict schema enforcement for LLM outputs)
- **PDF Processing:** pypdf + io.BytesIO (100% in-memory processing)

## Key Features

1. **Strict Structured Output:** Enforces strict Pydantic schemas, guaranteeing zero AI hallucinations regarding the JSON structure.
2. **Interactive Web Interface:** Modern, dark-themed responsive UI with drag-and-drop file upload, real-time loading animations, structured result cards, and one-click JSON file download.
3. **Dynamic Translation Pipeline:** Automatically generates a comprehensive executive summary and a list of actionable insights translated into a target language of your choice (via the `target_language` API query parameter, defaulting to Hungarian).
4. **Production-Ready Security:** Embedded IP-based rate limiting protects the service.
5. **Robust Upload Validation:** Strict 10 MB file size limit and dual MIME-type + file extension verification on every upload.

## API Usage Example

To extract data from a PDF and translate the summary/action items to German:

```http
POST /api/v1/extract?target_language=German HTTP/1.1
Content-Type: multipart/form-data

file: [your-pdf-file.pdf]
```

## Local Development Setup

### Prerequisites
- Python 3.11+
- A Google Gemini AI API Key (from Google AI Studio)

### 1. Clone the Repository
```bash
git clone https://github.com/hunorarato72/enterprise-pdf-extractor.git
cd enterprise-pdf-extractor
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
PROJECT_NAME="Enterprise PDF Data Extractor"
GOOGLE_API_KEY="your_actual_gemini_api_key_here"
```

### 3. Install Dependencies & Run
```bash
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

*   **UI:** Navigate to http://127.0.0.1:8000/ to view the web application.
*   **Docs:** Navigate to http://127.0.0.1:8000/docs to view the Swagger API docs.

### 4. Running the Tests
To run the automated test suite locally:
```bash
python -m pytest
```

## Docker Deployment

To build and run the container locally:

```bash
# Build the image
docker build -t pdf-extractor .

# Run the container
docker run -p 8000:8000 --env-file .env pdf-extractor
```

## Future Roadmap

- [x] **Automated Testing Suite:** Implement full unit and integration test coverage using `pytest` and `httpx`, utilizing mock LLM responses.
- [ ] **Native Multimodal PDF Processing:** Refactor the LLM pipeline to send the raw PDF file directly to Gemini's native document-processing engine (removing dependency on plain text extraction via `pypdf`).
