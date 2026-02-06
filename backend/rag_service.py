"""
RAG Service Module
Handles document embedding, storage in ChromaDB, and retrieval.
"""

# Fix for SSL Certificate Verify Failed error
# We rely on environment variables (HF_HUB_DISABLE_SSL_VERIFY) to handle this.
# This simple check ensures we respect the disable flag if set.
import os

if os.environ.get("HF_HUB_DISABLE_SSL_VERIFY") == "1":
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
        ssl._create_default_https_context = _create_unverified_https_context
    except AttributeError:
        pass

from sentence_transformers import SentenceTransformer
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from docx import Document
import hashlib



class RAGService:
    """Service class for RAG operations with ChromaDB and Nomic embeddings."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the RAG service.
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize Nomic embedding model
        # trust_remote_code=True is required for Nomic models
        self.embedding_model = SentenceTransformer(
            "nomic-ai/nomic-embed-text-v1.5", 
            trust_remote_code=True
        )
        
        # Collection name
        self.collection_name = "documents_nomic"
        
        # Get or create the collection
        # We don't verify dimensions here, we handle mismatches during add/query
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            # If collection exists with different settings, we might need to reset
            print(f"Warning initializing collection: {e}")
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def generate_embeddings(self, texts: list, is_document: bool = True) -> list:
        """
        Generate embeddings with proper Nomic prefixes.
        """
        prefix = "search_document: " if is_document else "search_query: "
        prefixed_texts = [prefix + text for text in texts]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(prefixed_texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text content from various file types."""
        text = ""
        if file_type == "pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif file_type == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif file_type == "docx":
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        return text
    
    def process_and_store_document(self, file_path: str, filename: str, file_type: str) -> dict:
        """Process a document and store it in ChromaDB."""
        try:
            # Extract text
            text = self.extract_text_from_file(file_path, file_type)
            if not text.strip():
                return {"success": False, "message": "No text content found"}
                
            # Split text
            chunks = self.text_splitter.split_text(text)
            
            # Generate embeddings manually
            embeddings = self.generate_embeddings(chunks, is_document=True)
            
            # Prepare IDs and Metadata
            doc_id = hashlib.md5(filename.encode()).hexdigest()[:8]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {"source": filename, "chunk_index": i, "total_chunks": len(chunks)}
                for i in range(len(chunks))
            ]
            
            # Add to ChromaDB
            try:
                self.collection.add(
                    documents=chunks,
                    embeddings=embeddings,
                    ids=ids,
                    metadatas=metadatas
                )
            except Exception as e:
                # Handle dimension mismatch by resetting collection
                if "dimension" in str(e).lower():
                    print("Dimension mismatch detected. Resetting collection for Nomic V2.")
                    self.client.delete_collection(self.collection_name)
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
                    # Retry add
                    self.collection.add(
                        documents=chunks,
                        embeddings=embeddings,
                        ids=ids,
                        metadatas=metadatas
                    )
                else:
                    raise e
            
            return {
                "success": True, 
                "message": f"Successfully processed {filename} with Nomic Embeddings", 
                "chunks_added": len(chunks)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def query_documents(self, query: str, n_results: int = 3) -> dict:
        """Query the vector database."""
        try:
            # Generate embedding for query
            query_embedding = self.generate_embeddings([query], is_document=False)
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            formatted_results = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "source": results["metadatas"][0][i]["source"],
                        "distance": results["distances"][0][i] if results["distances"] else 1.0,
                        "similarity": 1.0 - (results["distances"][0][i] if results["distances"] else 1.0)
                    })
            
            return {"success": True, "results": formatted_results}
            
        except Exception as e:
            return {"success": False, "message": f"Error querying: {str(e)}"}
            
    def get_collection_stats(self) -> dict:
        """Get collection stats."""
        try:
            return {"total_chunks": self.collection.count()}
        except:
            return {"total_chunks": 0}

    def get_all_documents(self) -> list:
        """Get a list of all unique documents in the collection."""
        try:
            # We can't query distinctly easily with Chroma's basic API efficiently for large datasets,
            # but for a small app, we can fetch all metadatas.
            # A more efficient way for large datasets would be to maintain a separate 'files' collection or SQLite table.
            # For this MVP, we'll fetch all metadatas (limit to 10000 chunks for safety).
            result = self.collection.get(include=["metadatas"], limit=10000)
            seen_files = set()
            file_list = []
            
            if result and result["metadatas"]:
                for meta in result["metadatas"]:
                    source = meta.get("source")
                    if source and source not in seen_files:
                        seen_files.add(source)
                        file_list.append(source)
            
            return sorted(list(file_list))
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []    

    def document_exists(self, filename: str) -> bool:
        """Check if a document with the given filename already exists."""
        try:
            # Verify if any chunk has this source
            result = self.collection.get(
                where={"source": filename},
                limit=1
            )
            return len(result["ids"]) > 0
        except:
            return False

    def delete_document(self, filename: str) -> dict:
        """Delete a document by filename."""
        try:
            # Delete entries where source equals filename
            self.collection.delete(
                where={"source": filename}
            )
            return {"success": True, "message": f"Document '{filename}' deleted"}
        except Exception as e:
            return {"success": False, "message": f"Error deleting document: {str(e)}"}

    def clear_collection(self) -> dict:
        """Clear the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return {"success": True, "message": "Collection cleared"}
        except Exception as e:
            return {"success": False, "message": str(e)}


# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create the RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
