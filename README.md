# ChatBot RAG Application

A modern RAG (Retention Augmented Generation) Chatbot built with Flask, Streamlit, and Google Gemini.

## Features
- **Document Upload**: Support for PDF, DOCX, and TXT files.
- **RAG Architecture**: Uses ChromaDB for vector storage and Nomic embeddings.
- **AI Answers**: Integrated with Google Gemini (gemini-2.0-flash) for natural language responses.
- **Dockerized**: Fully containerized for easy deployment.

## Prerequisites
- Docker & Docker Compose
- Google Gemini API Key

## Setup & Run

1.  **Clone the repository**
    ```bash
    git clone https://github.com/roshnaelsajohn/chatbot2026.git
    cd chatbot2026
    ```

2.  **Configure API Key**
    - Open `docker-compose.yml` and replace the `GOOGLE_API_KEY` value with your key.
    - OR set it as an environment variable in your shell.

3.  **Run with Docker** (Single command)
    ```bash
    docker-compose up --build -d
    ```

4.  **Access the App**
    - Frontend: http://localhost:8501
    - Backend API: http://localhost:5001/api

## Troubleshooting
- **Connection Refused**: Ensure backend is running (`docker ps`).
- **404 Model Not Found**: Ensure you are using a supported Gemini model (currently `gemini-2.0-flash`).