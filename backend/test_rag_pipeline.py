
import os
import sys

# Add current directory to path so we can import modules
sys.path.append('/app')

from rag_service import get_rag_service

def test_pipeline():
    print("🚀 Starting RAG Pipeline Test...")
    
    # 1. Create a dummy file
    test_content = """
    Nomic Embeddings are high-performance text embeddings.
    The secret password for the AI lab is 'Blueberry'.
    ChromaDB is an open-source vector database.
    """
    test_filename = "test_knowledge.txt"
    test_path = f"/tmp/{test_filename}"
    
    with open(test_path, "w") as f:
        f.write(test_content)
    
    print(f"📄 Created test file: {test_path}")

    # 2. Initialize Service
    try:
        rag_service = get_rag_service()
        print("✅ RAG Service initialized")
    except Exception as e:
        print(f"❌ Failed to init RAG Service: {e}")
        return

    # 3. Store Document
    print("📥 Storing document...")
    try:
        result = rag_service.process_and_store_document(test_path, test_filename, "txt")
        print(f"Store Result: {result}")
        if not result.get("success"):
            print("❌ Failed to store document")
            return
    except Exception as e:
        print(f"❌ Exception storing document: {e}")
        return

    # 4. Query Document
    query = "What is the secret password?"
    print(f"🔍 Querying: '{query}'")
    try:
        results = rag_service.query_documents(query, n_results=1)
        print("Query Results:", results)
        
        found = False
        if results.get("success") and results.get("results"):
            for res in results["results"]:
                print(f" -- Found chunk: {res['content'][:50]}...")
                if "Blueberry" in res['content']:
                    found = True
        
        if found:
            print("✅ TEST PASSED: Found the secret password in retrieved chunks!")
        else:
            print("❌ TEST FAILED: Did not find the secret password in chunks.")
            
    except Exception as e:
        print(f"❌ Exception querying: {e}")

if __name__ == "__main__":
    test_pipeline()
