import os
import google.generativeai as genai

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(self, query: str, context_chunks: list) -> str:
        """
        Generate a response using Gemini based on the query and retrieved context.
        """
        if not self.api_key:
            return "Error: Google Gemini API Key is missing. Please configure it in the backend environment variables."

        try:
            # Construct the prompt
            context_text = "\n\n".join([chunk["content"] for chunk in context_chunks])
            
            prompt = f"""You are a helpful AI assistant. Your task is to answer the user's question based ONLY on the provided context.
If the answer is not in the context, say "I cannot find the answer in the provided documents."

Context:
{context_text}

Question: 
{query}

Answer:"""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
