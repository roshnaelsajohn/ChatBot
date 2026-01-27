
import requests
import json

API_URL = "http://localhost:5000/api/chat"

def test_query(query):
    print(f"\n🔍 Testing Query: '{query}'")
    try:
        payload = {
            "message": query,
            "threshold": 0.0, # Set to 0 to see ALL scores
            "web_search": False, 
            "chat_mode": "document",
            "synthesize_response": False # Raw mode to see chunks
        }
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            chunks = data.get("chunks", [])
            print(f"   Chunks Found: {len(chunks)}")
            for i, chunk in enumerate(chunks[:3]): # Show top 3
                print(f"   [{i+1}] Source: {chunk.get('source')} | Similarity: {chunk.get('similarity')}")
                print(f"       Preview: {chunk.get('content')[:50]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_query("maple")
    test_query("Greenwood")
