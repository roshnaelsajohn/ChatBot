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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process and store in vector DB
        rag_service = get_rag_service()
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


# API endpoint - Chat Query
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Query the vector database with a user message.
    Expects JSON body with 'message' field.
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            "success": False,
            "message": "No message provided"
        }), 400
    
    query = data['message']
    n_results = data.get('n_results', 3)
    
    try:
        rag_service = get_rag_service()
        results = rag_service.query_documents(query, n_results)
        
        # Format response for chat
        if results["success"] and results["results"]:
            # Generate answer using Gemini (Instantiate here for thread safety)
            gemini_service = GeminiService()
            answer = gemini_service.generate_response(query, results["results"])
            
            # Calculate source counts for display
            source_counts = {}
            for r in results["results"]:
                source = r["source"]
                source_counts[source] = source_counts.get(source, 0) + 1
            
            # Format sources list with counts
            formatted_sources = [f"{src} ({count} chunks)" for src, count in source_counts.items()]
            
            response = {
                "success": True,
                "answer": answer,
                "sources": formatted_sources,
                "chunks": results["results"]
            }
        else:
            response = {
                "success": True,
                "answer": "I don't have any relevant information in my knowledge base. Please upload some documents first.",
                "sources": [],
                "chunks": []
            }
        
        return jsonify(response), 200
        
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
