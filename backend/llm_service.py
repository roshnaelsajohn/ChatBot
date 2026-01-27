import os
import google.generativeai as genai

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-lite-latest')

    def generate_response(self, query: str, context_chunks: list, source_type: str = "Document") -> str:
        """
        Generate a response using Gemini based on the query and retrieved context.
        source_type: 'Document', 'Web Search', or 'LLM Knowledge'
        """
        if not self.api_key:
            return "Error: Google Gemini API Key is missing. Please configure it in the backend environment variables."

        try:
            # Construct the prompt
            if source_type == "LLM Knowledge":
                prompt = f"""You are a helpful AI assistant. Answer the user's question using your general knowledge.
User Question: {query}
Answer:"""
            else:
                context_text = "\n\n".join([chunk["content"] for chunk in context_chunks])
                prompt = f"""You are a helpful AI assistant. Your task is to answer the user's question based ONLY on the provided context.
Source: {source_type}

Context:
{context_text}

Question: 
{query}

Answer:"""
            
            print(f"DEBUG: Using model {self.model.model_name}")
            print(f"DEBUG: Source Type: {source_type}")
            print(f"DEBUG: Prompt preview: {prompt[:500]}...")

            response = self.model.generate_content(prompt)
            # Prepend source tag to the answer if not already there (the user requested clear source tags)
            final_answer = f"[{source_type}] {response.text}"
            return final_answer
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
