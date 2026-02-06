import os
import google.generativeai as genai

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-001')

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

Instructions:
- Answer the user's question specifically and directly using **bullet points**.
- Only provide information that is strictly relevant to the question or topic given.
- Analyze the provided chunks. Use ONLY the chunks that are directly relevant to the user's {query}.
- IGNORE chunks that are from unrelated documents or do not answer the specific question.
- Do NOT generate empty list items, broken numbering, or whitespace-only lines.
- If the query is a keyword, summarize the key information related to it concisely.
- If the answer is not in the context, say "I cannot find the answer in the provided documents."

Context:
{context_text}

Question: 
{query}

Answer:"""
            
            print(f"DEBUG: Using model {self.model.model_name}")
            print(f"DEBUG: Source Type: {source_type}")
            
            # Retry logic for 429/Quota Exceeded
            max_retries = 3
            retry_delay = 5 # Start with 5 seconds (as per error message suggesting ~11s, we will ramp up)
            
            import time
            from google.api_core.exceptions import ResourceExhausted

            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    final_answer = f"[{source_type}] {response.text}"
                    return final_answer
                except ResourceExhausted:
                    print(f"WARN: Quota exceeded (Attempt {attempt+1}/{max_retries}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff: 5, 10, 20
                except Exception as e:
                    if "429" in str(e) or "Quota exceeded" in str(e) or "quota" in str(e).lower():
                         print(f"WARN: Quota/Rate Limit error (Attempt {attempt+1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                         time.sleep(retry_delay)
                         retry_delay *= 2
                    else:
                        raise e
            
            return "Error: Quota exceeded. Please try again later."
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
