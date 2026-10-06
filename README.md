# Enterprise PDF Data Extractor (AI Pipeline)

An asynchronous microservice built with **FastAPI** that extracts structured JSON data from PDF documents using the **Google Gemini 2.5 Flash** LLM, complete with an interactive, minimalist web UI.

---

## 🚀 Live Demo

The application is deployed live on **FastAPI Cloud**:

* **[Live Web Application](https://enterprise-pdf-extractor.fastapicloud.dev)**
* **[Interactive Swagger API Documentation](https://enterprise-pdf-extractor.fastapicloud.dev/docs)**

> **Note:** The endpoints are protected with an IP-based rate limiter (maximum 5 requests per minute).

---

## 🛠️ Tech Stack & Architecture

- **Backend Framework:** FastAPI (Python 3.11, fully asynchronous execution)
- **AI Engine:** Google Gemini 2.5 Flash (`langchain-google-genai` / Google GenAI SDK)
- **Schema & Validation:** Pydantic v2 (Guarantees deterministic, type-safe JSON output)
- **PDF Ingestion:** `pypdf` + `io.BytesIO` (100% in-memory processing in dedicated async worker threads)
- **Security & Rate Limiting:** `slowapi` (IP-based in-memory rate limiter)
- **Frontend UI:** Vanilla HTML5, CSS3 (minimalist dark grey & clean typography), JavaScript (Fetch API, drag-and-drop upload, one-click JSON export)
- **Deployment & Cloud:** **FastAPI Cloud** (`fastapi-cloud-cli`) & Docker containerization
- **Automated Testing:** `pytest` test suite with mocking for zero-token CI testing

---

## ⚡ Key Features

1. **Strict Structured Output:** Enforces strict Pydantic models with `with_structured_output`, eliminating AI hallucination regarding JSON schema structure.
2. **Asynchronous Thread Pooling:** CPU-bound PDF parsing is offloaded to worker threads via `asyncio.to_thread`, keeping the event loop responsive.
3. **Dynamic Translation Pipeline:** Extracts an executive summary and actionable takeaways, translated into the target language of your choice (`target_language` parameter, defaults to Hungarian).
4. **Minimalist Responsive Web UI:** Clean, dark grey interface with drag-and-drop file upload, real-time status feedback, structured metadata cards, and JSON export.
5. **Production Hardening:**
   - Dual-layer file validation (MIME-type check + file extension verification).
   - 10 MB maximum file size limit.
   - Built-in rate limiting (`5/minute` per IP).

---

## 📡 API Usage Example

To extract data from a PDF document with German executive summary and action items:

```http
POST /api/v1/extract?target_language=German HTTP/1.1
Host: enterprise-pdf-extractor.fastapicloud.dev
Content-Type: multipart/form-data

file: [your-document.pdf]
```

### Sample Response Payload:

```json
{
  "document_metadata": {
    "title": "Quarterly Financial Overview",
    "detected_language": "English",
    "document_type": "Financial Report"
  },
  "extracted_data": {
    "key_entities": ["Acme Corp", "Finance Department"],
    "important_numbers": [
      { "key": "Gesamtumsatz", "value": "1.250.000 EUR" },
      { "key": "EBITDA Marge", "value": "18.4%" }
    ]
  },
  "translation_pipeline": {
    "summary": "Umfassender vierteljährlicher Finanzbericht mit solidem Umsatzwachstum.",
    "action_items": [
      "Budgetüberprüfung für das nächste Quartal abschließen",
      "Kostenoptimierungsstrategie vorlegen"
    ]
  }
}
```

---

## 💻 Local Development Setup

### Prerequisites
- Python 3.11+
- Google Gemini API Key (from [Google AI Studio](https://aistudio.google.com/))

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

* **Web UI:** http://127.0.0.1:8000/
* **Interactive Docs:** http://127.0.0.1:8000/docs

### 4. Running Automated Tests
Run the unit test suite locally:
```bash
python -m pytest tests/ -v
```

---

## ☁️ Deployment

### 1. FastAPI Cloud (Recommended)
This service is natively deployed on **FastAPI Cloud**:

```bash
# Install / Upgrade the FastAPI Cloud CLI
pip install -U fastapi-cloud-cli

# Login to your account
fastapi login

# Deploy the application
fastapi deploy
```

Set secret environment variables:
```bash
fastapi cloud env set --secret GOOGLE_API_KEY "your_api_key_here"
```

### 2. Docker Deployment
To build and run the Docker container locally:

```bash
# Build Docker image
docker build -t enterprise-pdf-extractor .

# Run container with environment file
docker run -p 8000:8000 --env-file .env enterprise-pdf-extractor
```

---

## 🛣️ Future Roadmap

- [x] **Automated Testing Suite:** 100% test coverage using `pytest` and mock LLM calls.
- [x] **Cloud Deployment:** Production rollout on FastAPI Cloud.
- [ ] **Native Multimodal PDF Processing:** Direct PDF byte streaming into Gemini vision API.
