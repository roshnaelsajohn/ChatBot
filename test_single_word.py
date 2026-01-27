
import requests
import json

API_URL = "http://localhost:5000/api/chat"

def test_query(query):
    print(f"\n🔍 Testing Single Word Query: '{query}'")
    try:
        payload = {
            "message": query,
            "threshold": 0.55, # Using current default
            "web_search": False, # Strict RAG for debugging
            "talk_to_llm": False
        }
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            source = data.get("source_type", "Unknown")
            answer = data.get("answer", "")
            print(f"   Source Type: {source}")
            print(f"   Chunks Found: {len(data.get('chunks', []))}")
            if data.get('chunks'):
                print(f"   Top Similarity: {data['chunks'][0].get('similarity')}")
            print(f"   Answer Snippet: {answer[:100]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    # Test keywords known to be in the "Greenwood High School" text
    test_query("Greenwood")
    test_query("School")
    test_query("Springfield")
