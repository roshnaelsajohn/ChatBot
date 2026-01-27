
import requests
import json
import time

API_URL = "http://localhost:5000/api/chat"

def test_query(query, expected_source_type):
    print(f"\n🔍 Testing Query: '{query}'")
    try:
        payload = {
            "message": query,
            "threshold": 0.35,
            "web_search": True
        }
        start = time.time()
        response = requests.post(API_URL, json=payload)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            source = data.get("source_type", "Unknown")
            answer = data.get("answer", "")
            print(f"✅ Status: 200 (Time: {duration:.2f}s)")
            print(f"   Source Type: {source}")
            print(f"   Sources: {data.get('sources', [])}")
            print(f"   Answer Snippet: {answer[:100]}...")
            
            if source == expected_source_type:
                print("   Result: PASSED")
            else:
                print(f"   Result: FAILED (Expected {expected_source_type}, got {source})")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Hybrid RAG Verification...")
    
    # 1. Test Document Match (should match 'Blueberry')
    test_query("What is the secret password?", "Document")
    
    # 2. Test Document Match (should match 'Apple Pie')
    test_query("How to make apple pie", "Document")
    
    # 3. Test Web Search (Recent event/External knowledge)
    # Asking something random but searchable
    test_query("What is the capital of Australia?", "Web Search")
    
    # 4. Test LLM Knowledge (General concept or disable web search)
    # We can force LLM if we disable web search, but let's see if Web Search picks up general facts too.
    # Usually 'Capital of Australia' might be handled by web search or LLM depending on what DDGS returns.
    # Let's try explicit LLM fallback by disabling web search.
    print("\n🔍 Testing LLM Fallback (Web Search Disabled)")
    try:
        payload = {
            "message": "Write a haiku about coding",
            "threshold": 0.95, # High threshold to force miss
            "web_search": False
        }
        res = requests.post(API_URL, json=payload).json()
        print(f"   Source Type: {res.get('source_type')}")
        if res.get('source_type') == "LLM Knowledge":
             print("   Result: PASSED")
        else:
             print(f"   Result: FAILED (Expected LLM Knowledge, got {res.get('source_type')})")
    except:
        pass
