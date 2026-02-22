import anthropic
import os

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found")
else:
    client = anthropic.Anthropic(api_key=api_key)
    print("Available models:")
    for m in client.models.list():
        print(m.name)
