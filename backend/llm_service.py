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
                prompt = f"""You are a document assistant. Your task is to answer based ONLY on the provided context.
Source: {source_type}

Rules:
- Use ONLY the information provided in the Context below.
- Rewrite and structure the answer clearly.
- Do NOT copy large paragraphs from the context.
- When the answer contains a process → return it as numbered steps.
- When the answer contains a list of items → return it as bullet points.
- When providing definitions → use short concise sentences.
- If the answer is not in the context, reply: "I don’t have information about that in the provided documents."

Context:
{context_text}

Question: 
{query}

Answer:"""
            
            # Fallback Strategy
            models_to_try = [
                'gemini-2.0-flash-001',
                'gemini-2.0-flash-lite-preview-02-05',
                'gemini-flash-latest',
                'gemini-pro-latest'
            ]
            
            import time
            from google.api_core.exceptions import ResourceExhausted

            for model_name in models_to_try:
                try:
                    print(f"DEBUG: Attempting with model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Retry logic per model
                    max_retries = 2
                    retry_delay = 2
                    
                    for attempt in range(max_retries):
                        try:
                            response = self.model.generate_content(prompt)
                            final_answer = f"[{source_type}] {response.text}"
                            return final_answer
                        except ResourceExhausted:
                            print(f"WARN: Quota exceeded for {model_name}. Moving to next model...")
                            break # Break inner loop to try next model
                        except Exception as e:
                            if "429" in str(e) or "Quota exceeded" in str(e) or "quota" in str(e).lower():
                                 print(f"WARN: Rate Limit for {model_name} (Attempt {attempt+1}/{max_retries}). Retrying...")
                                 time.sleep(retry_delay)
                                 retry_delay *= 2
                            else:
                                raise e # Unknown error, maybe next model can handle? or just fail.
                                # Let's try next model for any error to be safe? 
                                # No, syntax errors etc should crash. But typically 500s or overloads might be model specific.
                                # Let's stick to Quota/429 being the trigger for retries, and ResourceExhausted for model switch.
                                
                    # If we exhausted retries for this model without success (but not ResourceExhausted which breaks early),
                    # we continue to next model.
                    
                except Exception as e:
                     print(f"Error with model {model_name}: {e}")
                     continue

            return "Error: All available models are currently overloaded or quota exceeded. Please try again later."
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
