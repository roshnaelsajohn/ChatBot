import os
from langsmith import Client, traceable
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class LangSmithEvalService:
    def __init__(self):
        self.api_key = os.environ.get("LANGSMITH_API_KEY")
        if not self.api_key:
            print("Warning: LANGSMITH_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = Client(api_key=self.api_key)

        self.llm = None
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_key:
             self.llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0,
                max_tokens=1024,
                timeout=None,
                max_retries=2,
                api_key=anthropic_key
            )

    @traceable(name="Evaluate Test Case Generation", run_type="chain")
    def evaluate_generation(self, original_story: str, generated_test_cases: str) -> dict:
        """
        Evaluate the generated test cases based on Completeness, Clarity, and Edge Cases
        using an LLM-as-a-judge.
        """
        if not self.llm:
            return {"success": False, "message": "LLM not configured for evaluation."}

        eval_prompt = PromptTemplate.from_template(
            """
            You are an expert QA Manager evaluating generated test cases.
            
            Original User Story:
            {original_story}
            
            Generated Test Cases:
            {generated_test_cases}
            
            Evaluate the test cases on the following 3 criteria on a scale of 1-10:
            1. Completeness: Does it cover all aspects of the user story?
            2. Clarity: Are the test steps and expected results clear?
            3. Edge Cases: Are edge cases and negative scenarios adequately covered?
            
            Provide only the scores in the following format:
            Completeness: [score]/10
            Clarity: [score]/10
            Edge Cases: [score]/10
            
            Then provide a brief 1-2 sentence overall summary.
            """
        )
        
        chain = eval_prompt | self.llm
        
        try:
             result = chain.invoke({
                 "original_story": original_story,
                 "generated_test_cases": generated_test_cases
             })
             
             return {
                 "success": True,
                 "evaluation": result.content
             }
        except Exception as e:
            return {
                "success": False,
                "message": f"Evaluation failed: {str(e)}"
            }
