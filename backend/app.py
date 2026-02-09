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
from monitoring_service import get_monitoring_service
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Initialize services (Lazy loading to avoid fork issues with gRPC/Chroma)
# gemini_service = GeminiService()

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'pptx', 'html', 'md'}

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
    n_results = data.get('n_results', 15)
    threshold = data.get('threshold', 0.55)
    synthesize_response = data.get('synthesize_response', True)

    # 'chat_mode' replaces 'web_search' and 'talk_to_llm'
    # Values: 'document', 'web', 'llm'
    chat_mode = data.get('chat_mode', 'document')
    
    try:
        rag_service = get_rag_service()
        gemini_service = GeminiService()
        monitor = get_monitoring_service()
        
        source_type = "LLM Knowledge"
        context_chunks = []
        formatted_sources = []
        
        # LOGIC BRANCHING BASED ON MODE
        if chat_mode == "llm":
            print("DEBUG: Mode = LLM Only")
            source_type = "LLM Knowledge"
            
        elif chat_mode == "web":
            print("DEBUG: Mode = Web Search Only")
            web_service = WebSearchService()
            web_results = web_service.search(query)
            
            if web_results:
                source_type = "Web Search"
                context_chunks = web_results
                formatted_sources = [f"Web: {r['title']} ({r['source']})" for r in web_results]
            else:
                print("DEBUG: Web search returned no results.")
                source_type = "LLM Knowledge" 
                
        else: 
            # OPTION 1: Grounded in Documents (RAG)
            print("DEBUG: Mode = Documents (Strict)")
            
            # 1. Query Documents
            results = rag_service.query_documents(query, n_results)
            
            if results["success"] and results["results"]:
                print(f"DEBUG: Default Threshold: {threshold}")
                
                # 2. Rerank Results (Hybrid Search)
                relevant_chunks = rag_service.rerank_results(results["results"], query, threshold)
                
                print(f"DEBUG: Hybrid Filter keeping {len(relevant_chunks)}/{len(results['results'])} chunks.")
                
                if relevant_chunks:
                    source_type = "Document"
                    context_chunks = relevant_chunks
                    
                    # Calculate source counts
                    source_counts = {}
                    for r in relevant_chunks:
                        source = r["source"]
                        source_counts[source] = source_counts.get(source, 0) + 1
                    formatted_sources = [f"{src}" for src in source_counts.keys()]

        # Generate Answer
        start_time = datetime.datetime.now()
        
        if not synthesize_response and source_type != "LLM Knowledge":
             print("DEBUG: Raw Retrieval Mode (Skipping LLM)")
             if context_chunks:
                 formatted_chunks = []
                 for i, chunk in enumerate(context_chunks):
                     content = chunk.get('content', '') or chunk.get('answer', '')
                     src = chunk.get('source', 'Unknown')
                     formatted_chunks.append(f"**Chunk {i+1}** (Source: {src}):\n{content}\n")
                 answer = f"**Raw Retrieval Results ({len(context_chunks)} chunks):**\n\n" + "\n---\n".join(formatted_chunks)
             else:
                 answer = "No relevant documents found."
        else:
             answer = gemini_service.generate_response(query, context_chunks, source_type)
        
        end_time = datetime.datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000

        # Log Interaction
        monitor.log_interaction(
            query=query,
            response=answer,
            source_type=source_type,
            sources=formatted_sources,
            latency_ms=latency
        )
        
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


@app.route("/api/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    """Delete a specific file."""
    try:
        rag_service = get_rag_service()
        result = rag_service.delete_document(filename)
        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error deleting file: {str(e)}"
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
