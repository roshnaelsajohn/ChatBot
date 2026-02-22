# ChatBot

A modern, containerized Chatbot application featuring **Hybrid RAG (Retrieval-Augmented Generation)**. It intelligently switches between strict document grounding, web search, and general LLM knowledge to provide accurate, reliable answers.

### Enhanced Retrieval-Augmented Generation (RAG) Model
Our latest enhancements to the RAG model focus on improving performance and accuracy. Key updates include:
- Fine-tuning with a larger dataset
- Reduced latency in response generation
- Improved understanding of context and nuance

### **Frontend**
*   **[React](https://react.dev/)**: Fast, single-page application (SPA).
*   **[Tailwind CSS](https://tailwindcss.com/)**: Modern, utility-first styling.
*   **Lucide Icons**: Beautiful, consistent iconography.

### **Backend**
*   **[Flask](https://flask.palletsprojects.com/)**: Lightweight REST API server.
*   **[Google Gemini API](https://ai.google.dev/)**: Powered by `gemini-flash-lite-latest` (or `gemini-2.0-flash-001`) for fast inference.
*   **[DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/)**: For real-time web search fallback.

### **RAG & Database**
*   **[ChromaDB](https://www.trychroma.com/)**: Open-source vector database for distinct document chunks.
*   **[Nomic Embeddings](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)**: High-performance `nomic-embed-text-v1.5` model for generating semantic vectors.
*   **[LangChain](https://www.langchain.com/)**: Utilized for text splitting and document processing.

### **Infrastructure**
*   **[Docker](https://www.docker.com/)**: Containerization for consistent environments.
*   **Docker Compose**: Orchestrates the Frontend and Backend services.

---

## 🛠 Key Features

### **1. Advanced Retrieval Engine (Hybrid RAG)**
*   **Hybrid Search**: 
    *   **Semantic Search**: For complex queries, uses vector similarity (strict threshold > `0.55`).
    *   **Keyword Boosting**: For short queries (e.g., "Street"), enforces exact keyword matches to prevent hallucination.
*   **Strict Grounding**: Explicitly commanded to ignore irrelevant chunks.
*   **Web Search Fallback**: Automatically searches the web if local documents are insufficient.

### **2. Robust LLM Handling**
*   **Rate Limit Protection**: Automatic exponential backoff for `429 Quota Exceeded` errors.
*   **Precision Prompting**: Engineered system prompts that:
    *   Enforce **bullet points** for readability.
    *   Ban empty lists and broken numbering.
    *   Require direct, concise answers without fluff.

### **3. Modern Document Management**
*   **Unified Dashboard**: View "Completed", "Pending", and "Failed" uploads in a single, filterable list.
*   **Smart Filtering**: Filter files by status (All, Completed, Pending, Failed).
*   **File Persistence**: Uploads survive container restarts via Docker volumes.
*   **Detailed Status**: Visual badges for upload progress and errors.

### **4. Interactive Chat UI**
*   **Source Citations**: Beautiful "Blue Badge" citations showing exactly which file (or web result) was used.
*   **Synthesize Toggle**: Option to get raw database chunks vs. a summarized AI answer (persisted preference).
*   **Clean Aesthetics**: Polished message bubbles, auto-scrolling, and responsive layout.

---

## 🏃‍♂️ How to Run

    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    
3.  **Start Application**:
    

---

## 📁 Project Structure

```
ChatBot/
├── backend/            # Flask API & RAG Logic
│   ├── app.py          # API Endpoints & Hybrid Search
│   ├── bl_service.py   # Rate-limited Gemini Integration
│   ├── rag_service.py  # ChromaDB & Embedding logic
│   └── web_search_service.py 
├── frontend-react/     # React UI
│   ├── src/
│   │   ├── components/ # ChatView, DocumentsView, Navigation
│   │   ├── api.js      # Frontend API Client
│   │   └── App.jsx     # Main Router
│   └── Dockerfile
├── docker-compose.yml  # Container Orchestration
└── README.md
```
