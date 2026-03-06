# ChatBot — Hybrid RAG AI Assistant

A modern, containerized AI chatbot powered by **Anthropic Claude** and **Hybrid RAG (Retrieval-Augmented Generation)**. It intelligently switches between strict document grounding, real-time web search, and general LLM knowledge to provide accurate, source-cited answers.

---

## 🧱 Tech Stack

### Languages
| Layer | Language |
|---|---|
| Backend | Python 3.x |
| Frontend | JavaScript (JSX / React) |
| Styling | CSS |
| Config | YAML, Dockerfile |

### Backend
| Library | Purpose |
|---|---|
| [Flask](https://flask.palletsprojects.com/) + Flask-CORS | REST API server |
| [Anthropic SDK](https://pypi.org/project/anthropic/) | LLM — Claude 3.5 Sonnet / Haiku |
| [ChromaDB](https://www.trychroma.com/) | Vector database |
| [Sentence Transformers](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) | `nomic-embed-text-v1.5` embeddings |
| [LangChain](https://www.langchain.com/) | Text splitting & semantic chunking |
| [LangSmith](https://smith.langchain.com/) | LLM trace observability |
| [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) | Real-time web search |
| pdfplumber / pypdf | PDF parsing |
| python-docx | DOCX parsing |
| python-pptx | PPTX parsing |
| BeautifulSoup4 | HTML parsing |
| python-dotenv | Environment variable loading |

### Frontend
| Library | Purpose |
|---|---|
| [React](https://react.dev/) | Single-page application |
| [Vite](https://vitejs.dev/) | Build tool |
| [Tailwind CSS](https://tailwindcss.com/) | Utility-first responsive styling |
| [Axios](https://axios-http.com/) | HTTP client (`api.js`) |
| Lucide Icons | Iconography |

### Infrastructure
| Tool | Purpose |
|---|---|
| Docker + Docker Compose | Container orchestration |
| Nginx | Frontend static file serving |

---

## 🛠 Key Features

### 1. Three Chat Modes
- **📄 Document** — Answers strictly grounded in uploaded files (Hybrid RAG)
- **🌐 Web Search** — Real-time DuckDuckGo results fed into Claude
- **🧠 LLM Knowledge** — Claude answers from its own training knowledge

### 2. Hybrid RAG Engine
- **Semantic Search** — Cosine similarity via ChromaDB (`threshold: 0.55`)
- **Semantic Chunking** — LangChain `SemanticChunker` for PDF/DOCX/PPTX; `MarkdownHeaderTextSplitter` for `.md`
- **Keyword Boosting** — Boosts exact keyword matches for short queries
- **Table Extraction** — Structured table-to-text conversion for PDFs and DOCX

### 3. Supported File Formats
`PDF` · `DOCX` · `PPTX` · `HTML` · `Markdown` · `TXT`

### 4. LLM Reliability
- **Model fallback chain**: `claude-3-5-sonnet` → `claude-3-5-haiku` → `claude-3-haiku`
- **Rate limit handling**: Automatically tries next model on `RateLimitError`
- **LangSmith tracing**: Every `generate_response()` call traced to `TestFlyAI` project

### 5. Document Management UI
- Drag-and-drop upload with progress tracking
- Duplicate detection before processing
- Filterable file list — All / Completed / Pending / Failed
- Persistent storage via Docker volumes

### 6. Mobile-Responsive Design
- **Bottom tab bar** replaces the sidebar on screens narrower than `768px`
- **Floating action button (FAB)** opens a slide-up bottom-sheet drawer for chat controls on mobile
- **Document list** collapses from a 4-column table to a compact **card list** on mobile
- All padding, font sizes, and icon sizes scale gracefully across breakpoints
- iOS safe-area inset support so the input bar is never hidden behind a notch

---

## 🏃‍♂️ How to Run

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose
- [Anthropic API key](https://console.anthropic.com) *(required)*
- [LangSmith API key](https://smith.langchain.com) *(optional — for tracing)*

### 1. Setup environment

```bash
cp .env.example .env
```

Fill in `.env`:

```env
# Required
ANTHROPIC_API_KEY=your_key_here

# Optional
OPENAI_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here
LANGSMITH_TRACING=true
LANGCHAIN_TRACING_V2=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=TestFlyAI
HF_HUB_DISABLE_SSL_VERIFY=1
```

### 2. Build and run

```bash
docker-compose up --build -d
```

### 3. Access

| Service | URL |
|---|---|
| 🖥️ Frontend | http://localhost:8501 |
| ⚙️ Backend API | http://localhost:5001 |

```bash
# Stop
docker-compose down
```

### Run locally (no Docker)

```bash
# Backend
source .venv/bin/activate
pip install -r backend/requirement.txt
cd backend && python app.py   # → http://localhost:5000

# Frontend (separate terminal)
cd frontend-react
npm install
npm run dev                   # → http://localhost:5173
```

---

## 📁 Project Structure

```
ChatBot/
├── backend/
│   ├── app.py                   # Flask REST API (endpoints: /chat, /publish, /files, /stats, /clear)
│   ├── llm_service.py           # Anthropic Claude integration + LangSmith @traceable
│   ├── rag_service.py           # ChromaDB, Nomic embeddings, hybrid search & reranking
│   ├── web_search_service.py    # DuckDuckGo search wrapper
│   ├── monitoring_service.py    # Request/response logging
│   ├── fix_ssl.py               # SSL certificate helper
│   ├── list_models.py           # Utility: list available Anthropic models
│   ├── requirement.txt          # Python dependencies
│   └── Dockerfile
│
├── frontend-react/              # Primary React UI (mobile-responsive)
│   └── src/
│       ├── App.jsx              # Main router + layout
│       ├── api.js               # Axios API client
│       └── components/
│           ├── ChatView.jsx     # Chat area + right-panel (desktop) / FAB drawer (mobile)
│           ├── ChatArea.jsx     # Message thread + responsive input bar
│           ├── MessageBubble.jsx # Individual message + source badges
│           ├── DocumentsView.jsx # Upload & management — table (desktop) / cards (mobile)
│           ├── Navigation.jsx   # Sidebar (desktop ≥768px) / bottom tab bar (mobile)
│           └── Header.jsx       # Compact top header bar
│
├── frontend/                    # Legacy Streamlit UI (unused in Docker)
│   └── streamlit_app.py
│
├── main.py                      # Standalone LangSmith tracing demo (OpenAI)
├── .env                         # Secrets (git-ignored ✅)
├── .env.example                 # Template (committed ✅)
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key |
| `OPENAI_API_KEY` | Optional | OpenAI key (used by `main.py`) |
| `LANGSMITH_API_KEY` | Optional | LangSmith tracing key |
| `LANGSMITH_PROJECT` | Optional | LangSmith project name |
| `LANGSMITH_TRACING` | Optional | Enable tracing (`true`) |
| `LANGCHAIN_TRACING_V2` | Optional | Required by `@traceable` decorator (`true`) |
| `LANGSMITH_ENDPOINT` | Optional | LangSmith API endpoint |
| `HF_HUB_DISABLE_SSL_VERIFY` | Optional | Disable HuggingFace SSL verify (`1`) |
| `VITE_API_BASE_URL` | Optional | Frontend API base URL (local dev) |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/hello` | Health check |
| `POST` | `/api/publish` | Upload & index a document |
| `GET` | `/api/files` | List all indexed files |
| `DELETE` | `/api/files/<filename>` | Delete a specific file |
| `POST` | `/api/chat` | Send a chat query |
| `GET` | `/api/stats` | ChromaDB collection stats |
| `POST` | `/api/clear` | Clear all documents |
