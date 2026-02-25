import os
import anthropic

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

print("Listing available models...")
try:
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
