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
    n_results = data.get('n_results', 15)
    threshold = data.get('threshold', 0.55) # Aggressively raised to 0.55

    # 'chat_mode' replaces 'web_search' and 'talk_to_llm'
    # Values: 'document', 'web', 'llm'
    chat_mode = data.get('chat_mode', 'document')
    
    try:
        rag_service = get_rag_service()
        gemini_service = GeminiService()
        
        source_type = "LLM Knowledge"
        context_chunks = []
        formatted_sources = []
        
        # LOGIC BRANCHING BASED ON MODE
        if chat_mode == "llm":
            # OPTION 3: Bypass RAG, chat directly with LLM
            print("DEBUG: Mode = LLM Only")
            source_type = "LLM Knowledge"
            # No context chunks needed for pure LLM chat
            
        elif chat_mode == "web":
            # OPTION 2: Web Search Only
            print("DEBUG: Mode = Web Search Only")
            web_service = WebSearchService()
            web_results = web_service.search(query)
            
            if web_results:
                source_type = "Web Search"
                context_chunks = web_results
                formatted_sources = [f"Web: {r['title']} ({r['source']})" for r in web_results]
            else:
                # If web search fails, what do we do?
                # For strict mode, we might just say "No web results found".
                # But typically we fall back to LLM or just return empty.
                # Let's fallback to LLM knowledge but tag it.
                print("DEBUG: Web search returned no results.")
                source_type = "LLM Knowledge" # Soft fallback if web fails?
                
        else: 
            # OPTION 1: Grounded in Documents (RAG) - Default 'document'
            print("DEBUG: Mode = Documents (Strict)")
            
            # 1. Query Documents
            results = rag_service.query_documents(query, n_results)
            
            if results["success"] and results["results"]:
                print(f"DEBUG: Default Threshold: {threshold}")
                
                # HYBRID SEARCH LOGIC
                # For short queries (keywords), we enforce exact matches to prevent semantic drift.
                is_keyword_search = len(query.split()) < 3
                refined_results = []
                
                for i, r in enumerate(results["results"]):
                     score = round(r.get('similarity', 0.0), 3)
                     src = r.get('source', 'unknown')
                     content = r.get('content', '')
                     snippet = content[:50].replace('\n', ' ')
                     
                     # Check for exact keyword match
                     has_keyword = query.lower() in content.lower()
                     
                     print(f"DEBUG: Chunk {i} | Score: {score} | Keyword Match: {has_keyword} | File: {src} | Content: {snippet}...")
                     
                     # DECISION LOGIC:
                     # 1. If it's a keyword search, REQUIRE the keyword OR a very high semantic score (>0.65)
                     if is_keyword_search:
                         if has_keyword:
                             # Boost score for exact match if it was borderline
                             if score >= 0.35: # Lower retrieval floor for exact matches
                                 refined_results.append(r)
                         elif score >= 0.65:
                             # Keep high-confidence semantic matches even without keyword
                             refined_results.append(r)
                         else:
                             print(f"DEBUG: Dropping Chunk {i} (No keyword match & score {score} < 0.65)")
                     else:
                         # Standard Semantic Search for longer queries
                         if score >= threshold:
                             refined_results.append(r)

                relevant_chunks = refined_results
                
                print(f"DEBUG: Hybrid Filter keeping {len(relevant_chunks)}/{len(results['results'])} chunks.")
                
                if relevant_chunks:
                    source_type = "Document"
                    context_chunks = relevant_chunks
                    
                    # Calculate source counts
                    source_counts = {}
                    for r in relevant_chunks:
                        source = r["source"]
                        source_counts[source] = source_counts.get(source, 0) + 1
                    formatted_sources = [f"{src} ({count} chunks)" for src, count in source_counts.items()]
            
            # STRICT GROUNDING: If no doc found, do NOT fallback to web or LLM.
            if source_type != "Document":
                 # Ensure we don't accidentally use LLM Knowledge mode
                 source_type = "Document" 
                 formatted_sources = [] 
                 # prompt will handle empty context -> "I cannot find the answer"
                 
        if "LLM" in source_type and chat_mode == "llm":
            # For strict LLM mode, we MUST synthesize (raw retrieval makes no sense for pure generation)
            answer = gemini_service.generate_response(query, context_chunks, source_type)
        else:
            # Check if user wants raw retrieval (No LLM)
            synthesize_response = data.get('synthesize_response', True)
            
            if not synthesize_response and source_type != "LLM Knowledge":
                print("DEBUG: Raw Retrieval Mode (Skipping LLM)")
                if context_chunks:
                    formatted_chunks = []
                    for i, chunk in enumerate(context_chunks):
                        content = chunk.get('content', '') or chunk.get('answer', '') # Handle web/doc difference
                        src = chunk.get('source', 'Unknown')
                        formatted_chunks.append(f"**Chunk {i+1}** (Source: {src}):\n{content}\n")
                    answer = f"**Raw Retrieval Results ({len(context_chunks)} chunks):**\n\n" + "\n---\n".join(formatted_chunks)
                else:
                    answer = "No relevant documents found."
            else:
                 # Standard RAG Generation
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
