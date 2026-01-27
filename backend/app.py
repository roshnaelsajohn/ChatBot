"""
Flask Backend for Chatbot RAG Application
Provides API endpoints for file upload, document publishing, and chat queries.
"""

import os
import tempfile
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from rag_service import get_rag_service
from llm_service import GeminiService

from web_search_service import WebSearchService

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Initialize services (Lazy loading to avoid fork issues with gRPC/Chroma)
# gemini_service = GeminiService()

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    """Get the file type from filename."""
    return filename.rsplit('.', 1)[1].lower()


# API endpoint - Hello (keeping original)
@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({
        "message": "Hello from the Python backend!"
    })


# API endpoint - Upload and Publish Document
@app.route("/api/publish", methods=["POST"])
def publish_document():
    """
    Upload a file and publish it to the vector database.
    Expects a multipart form with a 'file' field.
    """
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "message": "No file provided"
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        
        # Check for duplicates before expensive processing
        rag_service = get_rag_service()
        if rag_service.document_exists(filename):
             return jsonify({
                "success": False,
                "message": f"File '{filename}' already exists in the database."
            }), 409
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process and store in vector DB
        file_type = get_file_type(filename)
        result = rag_service.process_and_store_document(file_path, filename, file_type)
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error processing file: {str(e)}"
        }), 500


# API endpoint - List Files
@app.route("/api/files", methods=["GET"])
def list_files():
    """List all uploaded files."""
    try:
        rag_service = get_rag_service()
        files = rag_service.get_all_documents()
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint - Chat Query
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Query the vector database with a user message.
    Expects JSON body with 'message' field.
    Supports optional parameters: 'n_results', 'threshold', 'web_search'.
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            "success": False,
            "message": "No message provided"
        }), 400
    
    query = data['message']
    n_results = data.get('n_results', 3)
    threshold = data.get('threshold', 0.55)
    web_search_enabled = data.get('web_search', True)
    talk_to_llm = data.get('talk_to_llm', False)
    
    try:
        rag_service = get_rag_service()
        gemini_service = GeminiService()
        
        source_type = "LLM Knowledge"
        context_chunks = []
        formatted_sources = []
        
        # LOGIC BRANCHING
        if talk_to_llm:
            # OPTION 1: Bypass RAG, chat directly with LLM
            print("DEBUG: Mode = Talk to LLM (Bypassing Documents)")
            source_type = "LLM Knowledge"
            # No context chunks needed for pure LLM chat
        else:
            # OPTION 2: Grounded in Documents (RAG)
            print("DEBUG: Mode = Grounded in Documents")
            
            # 1. Query Documents
            results = rag_service.query_documents(query, n_results)
            
            max_similarity = 0.0
            found_high_quality_doc = False
            
            if results["success"] and results["results"]:
                max_similarity = max([r.get("similarity", 0.0) for r in results["results"]])
                print(f"DEBUG: Max Similarity: {max_similarity} (Threshold: {threshold})")
                
                if max_similarity >= threshold:
                    source_type = "Document"
                    context_chunks = results["results"]
                    found_high_quality_doc = True
                    
                    # Calculate source counts
                    source_counts = {}
                    for r in results["results"]:
                        source = r["source"]
                        source_counts[source] = source_counts.get(source, 0) + 1
                    formatted_sources = [f"{src} ({count} chunks)" for src, count in source_counts.items()]
            
            # 2. Fallback to Web Search (if enabled and no good doc found)
            if not found_high_quality_doc and web_search_enabled:
                print("DEBUG: Low/No document match, attempting Web Search...")
                web_service = WebSearchService()
                web_results = web_service.search(query)
                
                if web_results:
                    source_type = "Web Search"
                    context_chunks = web_results
                    formatted_sources = [f"Web: {r['title']} ({r['source']})" for r in web_results]
            
            # 3. STRICT GROUNDING CHECK
            # If we are in "RAG Mode" (talk_to_llm=False) and we have NO documents and NO web results,
            # we should NOT fall back to LLM Knowledge. We should tell the user we couldn't find anything.
            if source_type == "LLM Knowledge":
                # This means we didn't find a Doc and didn't find Web results (or web disabled)
                # But since talk_to_llm is False, we typically want to say "Not found".
                # HOWEVER, the prompt in llm_service handles "I cannot find the answer".
                # So we pass an empty context to Gemini with source_type="Document" (effectively),
                # and let it say "I cannot find..."
                source_type = "Document" # Force "Document" mode with empty context so it fails gracefully
                formatted_sources = []
                 
        # 4. Generate Answer
        answer = gemini_service.generate_response(query, context_chunks, source_type)
        
        response = {
            "success": True,
            "answer": answer,
            "sources": formatted_sources,
            "chunks": context_chunks,
            "source_type": source_type
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error processing query: {str(e)}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error processing query: {str(e)}"
        }), 500


# API endpoint - Get Collection Stats
@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get statistics about the document collection."""
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_collection_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint - Clear Collection
@app.route("/api/clear", methods=["POST"])
def clear_collection():
    """Clear all documents from the collection."""
    try:
        rag_service = get_rag_service()
        result = rag_service.clear_collection()
        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error clearing collection: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("🚀 Starting Chatbot RAG Backend...")
    print("📁 Supported file types:", ALLOWED_EXTENSIONS)
    print("🔗 API Endpoints:")
    print("   - GET  /api/hello  - Health check")
    print("   - POST /api/publish - Upload and index document")
    print("   - POST /api/chat   - Query documents")
    print("   - GET  /api/stats  - Collection statistics")
    print("   - POST /api/clear  - Clear all documents")
    print("   - POST /api/clear  - Clear all documents")
    # Disable reloader to prevent "terminate called without an active exception"
    # This happens because grpc/chroma are not fork-safe when used with Flask reloader in Docker
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
