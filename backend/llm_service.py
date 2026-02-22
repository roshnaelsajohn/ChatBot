import os
import anthropic
from langsmith import traceable

class GeminiService:
    """
    LLM service — now powered by Anthropic Claude.
    Class name kept as-is so existing imports in app.py continue to work.
    """

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    @traceable(name="Claude LLM Response", run_type="llm")
    def generate_response(self, query: str, context_chunks: list, source_type: str = "Document") -> str:
        """
        Generate a response using Claude based on the query and retrieved context.
        source_type: 'Document', 'Web Search', or 'LLM Knowledge'
        """
        if not self.client:
            return "Error: ANTHROPIC_API_KEY is missing. Please configure it in the backend environment variables."

        try:
            # Build prompt
            if source_type == "LLM Knowledge":
                system_prompt = "You are a helpful AI assistant. Answer the user's question using your general knowledge."
                user_content = query
            else:
                context_text = "\n\n".join([chunk["content"] for chunk in context_chunks])
                system_prompt = (
                    "You are a document assistant. Your task is to answer based ONLY on the provided context.\n\n"
                    "Rules:\n"
                    "- Use ONLY the information provided in the Context below.\n"
                    "- Rewrite and structure the answer clearly.\n"
                    "- Do NOT copy large paragraphs from the context.\n"
                    "- When the answer contains a process → return it as numbered steps.\n"
                    "- When the answer contains a list of items → return it as bullet points.\n"
                    "- When providing definitions → use short concise sentences.\n"
                    "- If the answer is not in the context, reply: \"I don't have information about that in the provided documents.\""
                )
                user_content = f"Source: {source_type}\n\nContext:\n{context_text}\n\nQuestion:\n{query}"

            # Fallback model list (most capable → lightest)
            models_to_try = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-haiku-20240307",
            ]

            for model_name in models_to_try:
                try:
                    print(f"DEBUG: Attempting with model: {model_name}")
                    response = self.client.messages.create(
                        model=model_name,
                        max_tokens=1024,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_content}],
                    )
                    answer = response.content[0].text
                    return f"[{source_type}] {answer}"

                except anthropic.RateLimitError:
                    print(f"WARN: Rate limit hit for {model_name}. Trying next model...")
                    continue
                except anthropic.APIStatusError as e:
                    print(f"WARN: API error for {model_name}: {e}. Trying next model...")
                    continue
                except Exception as e:
                    print(f"Error with model {model_name}: {e}")
                    continue

            return "Error: All available Claude models are rate-limited or unavailable. Please try again later."

        except Exception as e:
            return f"Error generating response: {str(e)}"
