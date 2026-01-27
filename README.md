# 🤖 AI RAG Chatbot

A modern, containerized Chatbot application featuring **Hybrid RAG (Retrieval-Augmented Generation)**. It intelligently switches between strict document grounding, web search, and general LLM knowledge.

## 🚀 Technologies Used

### **Frontend**
*   **[Streamlit](https://streamlit.io/)**: For a fast, interactive, and beautiful user interface.
*   **Python**: Core logic.
*   **Custom CSS**: For a modern, dark-themed aesthetic.

### **Backend**
*   **[Flask](https://flask.palletsprojects.com/)**: Lightweight REST API server.
*   **[Google Gemini API](https://ai.google.dev/)**: Powered by `gemini-flash-lite-latest` (or `gemini-1.5-flash`) for fast and efficient inference.
*   **[DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/)**: For real-time web search fallback.

### **RAG & Database**
*   **[ChromaDB](https://www.trychroma.com/)**: Open-source vector database for distinct document chunks.
*   **[Nomic Embeddings](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)**: High-performance `nomic-embed-text-v1.5` model for generating semantic vectors.
*   **[LangChain](https://www.langchain.com/)**: utilized for `RecursiveCharacterTextSplitter` to chunk documents intelligently.
*   **Sentence Transformers**: For local embedding generation.

### **Infrastructure**
*   **[Docker](https://www.docker.com/)**: Containerization for consistent environments.
*   **Docker Compose**: Orchestrates the Frontend and Backend services.

---

## 🛠 Features

1.  **Hybrid RAG Logic**:
    *   **Documents**: strict matching with similarity thresholds (default `0.55`).
    *   **Web Search**: Auto-fallback if documents don't contain the answer.
    *   **LLM Knowledge**: Fallback if all else fails (or explicitly toggled).
2.  **File Support**: Upload PDF, DOCX, and TXT files.
3.  **Duplicate Protection**: Prevents re-uploading the same file.
4.  **Persistent Storage**: Vector database persists restarts via Docker volumes.
5.  **Smart UI**: "Ask Documents" vs "Ask General Knowledge" toggle.

---

## 🏃‍♂️ How to Run

1.  **Prerequisites**:
    *   Docker & Docker Compose installed.
    *   A Google Gemini API Key.

2.  **Setup Environment**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    HF_HUB_DISABLE_SSL_VERIFY=1  # Optional: Fixes some SSL issues with downloading models
    ```

3.  **Start Application**:
    ```bash
    docker-compose up -d --build
    ```

4.  **Access**:
    *   **Frontend**: [http://localhost:8501](http://localhost:8501)
    *   **Backend API**: [http://localhost:5000/api/hello](http://localhost:5000/api/hello)

---

## 📁 Project Structure

```
ChatBot/
├── backend/            # Flask API & RAG Logic
│   ├── app.py          # API Endpoints
│   ├── rag_service.py  # ChromaDB & Embedding logic
│   ├── llm_service.py  # Gemini Integration
│   ├── web_search_service.py # DuckDuckGo Integration
│   └── Dockerfile
├── frontend/           # Streamlit UI
│   ├── streamlit_app.py
│   └── Dockerfile
├── docker-compose.yml  # Container Orchestration
└── README.md
```