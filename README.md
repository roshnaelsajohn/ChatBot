# ChatBot — Hybrid RAG AI Assistant

A modern, containerized chatbot featuring **Hybrid RAG (Retrieval-Augmented Generation)**. It intelligently switches between strict document grounding, web search, and general LLM knowledge to provide accurate, reliable answers.

---

## 🧱 Tech Stack

### **Frontend**
- **[React](https://react.dev/)** — Fast, single-page application (SPA)
- **[Tailwind CSS](https://tailwindcss.com/)** — Modern utility-first styling
- **Lucide Icons** — Consistent iconography

### **Backend**
- **[Flask](https://flask.palletsprojects.com/)** — Lightweight REST API server
- **[Anthropic Claude API](https://www.anthropic.com/)** — LLM powered by `claude-3-5-sonnet` with automatic fallback to `claude-3-5-haiku` and `claude-3-haiku`
- **[DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/)** — Real-time web search fallback

### **RAG & Database**
- **[ChromaDB](https://www.trychroma.com/)** — Vector database for document chunks
- **[Nomic Embeddings](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)** — `nomic-embed-text-v1.5` for semantic vector generation
- **[LangChain](https://www.langchain.com/)** — Text splitting and processing

### **Observability**
- **[LangSmith](https://smith.langchain.com/)** — Full LLM trace logging via `@traceable`, tracked under the `TestFlyAI` project

### **Infrastructure**
- **[Docker](https://www.docker.com/)** & **Docker Compose** — Containerised services

---

## 🛠 Key Features

### 1. Advanced Retrieval Engine (Hybrid RAG)
- **Semantic Search** — Vector similarity with a strict `0.55` threshold for complex queries
- **Keyword Boosting** — Exact keyword matching for short queries to prevent hallucination
- **Web Search Fallback** — Automatically searches the web when local documents are insufficient
- **Three Chat Modes** — `Document`, `Web`, or `LLM Knowledge`

### 2. Robust LLM Handling (Claude)
- **Model Fallback Chain** — `claude-3-5-sonnet` → `claude-3-5-haiku` → `claude-3-haiku`
- **Rate Limit Protection** — Automatically tries the next model on `RateLimitError`
- **Precision Prompting** — Structured system prompts for bullet points, numbered steps, and direct answers

### 3. LangSmith Tracing
- Every `generate_response()` call is traced with `@traceable`
- Traces appear in **LangSmith → Project: TestFlyAI**

### 4. Document Management
- Upload **PDF, DOCX, PPTX, HTML, Markdown, TXT**
- Smart deduplication — rejects duplicate file uploads
- File persistence via Docker volumes (survives restarts)
- Filterable dashboard — All / Completed / Pending / Failed

### 5. Interactive Chat UI
- Source citations showing which document/web result was used
- Synthesize toggle — raw database chunks vs. AI-summarised answer
- Polished message bubbles with auto-scroll

---

## 🏃‍♂️ How to Run

### Prerequisites
- Docker & Docker Compose
- Anthropic API key — [console.anthropic.com](https://console.anthropic.com)
- LangSmith API key — [smith.langchain.com](https://smith.langchain.com) *(optional, for tracing)*

### 1. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here         # optional

LANGSMITH_TRACING=true
LANGCHAIN_TRACING_V2=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=TestFlyAI
```

### 2. Start the application

```bash
docker-compose up --build -d
```

### 3. Access

| Service | URL |
|---|---|
| 🖥️ Frontend | http://localhost:8501 |
| ⚙️ Backend API | http://localhost:5001 |
| 📊 LangSmith | https://smith.langchain.com |

### Stop

```bash
docker-compose down
```

### Run locally (without Docker)

```bash
# Backend
source .venv/bin/activate
cd backend && python app.py

# Frontend (separate terminal)
cd frontend-react
npm install
npm run dev
```

---

## 📁 Project Structure

```
ChatBot/
├── backend/
│   ├── app.py                  # Flask API endpoints
│   ├── llm_service.py          # Anthropic Claude integration + LangSmith tracing
│   ├── rag_service.py          # ChromaDB & Nomic embedding logic
│   ├── web_search_service.py   # DuckDuckGo search
│   ├── monitoring_service.py   # Interaction logging
│   └── requirement.txt
├── frontend-react/             # React UI
│   ├── src/
│   │   ├── components/         # ChatView, DocumentsView, Navigation
│   │   ├── api.js              # Frontend API client
│   │   └── App.jsx             # Main router
│   └── Dockerfile
├── main.py                     # Standalone LangSmith tracing demo
├── .env                        # Secrets (git-ignored)
├── .env.example                # Template (safe to commit)
├── docker-compose.yml
└── README.md
```

---

## 🔐 Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `LANGSMITH_API_KEY` | Optional | LangSmith tracing key |
| `LANGSMITH_PROJECT` | Optional | LangSmith project name (default: `TestFlyAI`) |
| `LANGSMITH_TRACING` | Optional | Enable tracing (`true`/`false`) |
| `LANGCHAIN_TRACING_V2` | Optional | Required by `@traceable` decorator (`true`) |
| `HF_HUB_DISABLE_SSL_VERIFY` | Optional | Disable SSL for HuggingFace downloads (`1`) |
