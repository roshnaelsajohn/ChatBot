import os
from langsmith import traceable
import anthropic
from dotenv import load_dotenv
from jira_service import JiraService

load_dotenv()

class TestCaseService:
    def __init__(self):
        self.jira_service = JiraService()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    @traceable(name="Generate Test Cases", run_type="chain")
    def generate_from_jira(self, issue_key: str) -> dict:
        """
        Fetch Jira issue and generate test cases.
        """
        # 1. Fetch User Story
        jira_result = self.jira_service.get_user_story_details(issue_key)
        
        if not jira_result["success"]:
            return {
                "success": False,
                "message": jira_result["message"]
            }
            
        summary = jira_result["summary"]
        description = jira_result["description"]
        
        # 2. Generate Test Cases
        return self._generate_test_cases(issue_key, summary, description)

    @traceable(name="Generate Test Cases from Text", run_type="chain")
    def generate_from_text(self, summary: str, description: str) -> dict:
         return self._generate_test_cases("Custom Input", summary, description)

    @traceable(name="LLM Test Case Generation", run_type="llm")
    def _generate_test_cases(self, key: str, summary: str, description: str) -> dict:
        if not self.client:
            return {
                "success": False,
                "message": "Error: ANTHROPIC_API_KEY is missing."
            }
            
        system_prompt = (
            "You are a QA Engineer expert. "
            "Given a User Story summary and description, generate comprehensive Test Cases. "
            "Include Positive, Negative, and Edge Cases. "
            "Format your output clearly using markdown with headings, bullet points, and numbered lists."
        )
        
        user_content = f"Issue Key/Title: {key}\nSummary: {summary}\nDescription:\n{description}\n\nPlease generate the test cases."
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            answer = response.content[0].text
            return {
                "success": True,
                "test_cases": answer,
                "jira_info": {
                    "key": key,
                    "summary": summary,
                    "description": description
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating test cases: {str(e)}"
            }
