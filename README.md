# Enterprise PDF Data Extractor (AI Pipeline)

An asynchronous microservice built with **FastAPI** and **Docker** that extracts structured JSON data from raw PDF documents using the **Google Gemini 2.5 Flash** LLM. 

## Live Demo

The application is fully dockerized and deployed on the **DigitalOcean App Platform**. You can interact with the live API and view the auto-generated documentation via Swagger UI:
**[CLICK HERE FOR LIVE SWAGGER UI](https://enterprise-data-extractor-j6jzn.ondigitalocean.app/docs)**

*(Note:The live endpoint is secured with an IP-based rate limiter allowing a maximum of 5 requests per minute).*

## Tech Stack & Architecture

- **Backend Framework:** FastAPI (Python 3.11, fully asynchronous execution)
- **AI Engine:** Google GenAI SDK / LangChain (Gemini 2.5 Flash)
- **Containerization:** Docker (Containerized using a lightweight python:3.11-slim base image)
- **Security & Rate Limiting:** slowapi (In-memory rate limiting using the limits engine)
- **Data Validation:** Pydantic (Strict schema enforcement, ensuring type safety for LLM outputs)
- **PDF Processing:** pypdf + io.BytesIO (100% in-memory processing)

## Key Features

1. **Strict Structured Output:** Enforces strict Pydantic schemas. This guarantees zero AI hallucinations regarding the JSON structure and ensures frontend compatibility.
2. **Language-Agnostic Processing:** Capable of parsing and understanding financial, or corporate PDFs in any language.
3. **Automated Translation Pipeline:** Automatically generates a comprehensive executive summary and a list of actionable insights translated into Hungarian, regardless of the source document's language.
4. **Production-Ready Security:** Embedded IP-based rate limiting protects the service.

## Local Development Setup

### Prerequisites
- Python 3.11+ (Using uv package manager is recommended)
- A Google Gemini AI API Key (from Google AI Studio)

### 1. Clone the Repository
```bash
git clone [https://github.com/hunorarato72/enterprise-pdf-extractor.git](https://github.com/hunorarato72/enterprise-pdf-extractor.git)
cd enterprise-pdf-extractor
```

### 2. Environment Setup
Create a .env file in the root directory:
```env
PROJECT_NAME="Enterprise PDF Data Extractor"
GOOGLE_API_KEY="your_actual_gemini_api_key_here"
```

### 3. Install Dependencies & Run
Using uv:
```bash
uv venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.\.venv\Scripts\activate

uv pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open your browser and navigate to http://127.0.0.1:8000/docs to test it locally.

## Docker Deployment

The project includes a production-ready Dockerfile and .dockerignore. To build and run the container locally:

```bash
# Build the image
docker build -t pdf-extractor .

# Run the container
docker run -p 8000:8000 --env-file .env pdf-extractor
```

## Future Roadmap (v2.0)

- [ ] **Automated Testing Suite:** Implement full unit and integration test coverage using `pytest` and `httpx`, utilizing mock LLM responses.
- [ ] **Native Multimodal PDF Processing:** Refactor the LLM pipeline to send the raw PDF file directly to Gemini's native document-processing engine (removing dependency on plain text extraction via `pypdf`).
- [ ] **Dynamic Target Languages:** Support user-configurable target translation languages dynamically via API query parameters rather than hardcoded fields.
- [ ] **Upload Size & Type Verification:** Add defensive validation to restrict uploaded files to a maximum size (e.g., 10MB) and strictly verify MIME-type headers.
