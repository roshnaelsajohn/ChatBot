import os
import argparse
import re
from langsmith import evaluate
from test_case_service import TestCaseService
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def generate_and_evaluate(inputs: dict) -> dict:
    summary = inputs.get("summary")
    description = inputs.get("description")
    tc_service = TestCaseService()
    result = tc_service.generate_from_text(summary, description)
    if result["success"]:
        return {"generated_test_cases": result["test_cases"]}
    else:
        return {"generated_test_cases": f"Generation Failed: {result.get('message')}"}

def evaluate_security(run, example) -> dict:
    """Evaluates Security and Privacy aspects of the test cases."""
    generated = run.outputs["generated_test_cases"]
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
         return {"key": "Security_Score", "score": 0, "comment": "No Auth Key"}
         
    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",
        temperature=0,
        api_key=anthropic_key
    )

    eval_prompt = PromptTemplate.from_template(
        """
        You are a Security Auditor. Evaluate the following generated test cases for Security & Privacy.
        
        GENERATED TEST CASES:
        {generated}
        
        Rate on a scale of 1-10 based on:
        1. Access Control: Do they verify authorization/authentication?
        2. Data Privacy: Do they mention masking sensitive data (e.g. passwords)?
        3. Threat Modeling: Do they consider common attacks (SQLi, XSS) where relevant?

        Format your response exactly like this:
        Security_Score: [1-10]/10
        Reasoning: [Brief explanation]
        """
    )
    
    chain = eval_prompt | llm
    try:
         result = chain.invoke({"generated": generated})
         content = result.content
         score = 0
         match = re.search(r"Security_Score:\s*(\d+)", content)
         if match:
             score = int(match.group(1)) / 10.0
         return {"key": "Security_Privacy_Score", "score": score, "comment": content}
    except Exception as e:
         return {"key": "Security_Privacy_Score", "score": 0, "comment": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", help="Dataset name or ID")
    args = parser.parse_args()

    # Use the standard dataset from .env
    dataset_to_run = args.dataset or os.environ.get("LANGSMITH_TARGET_DATASET_ID", "testFly")

    print(f"🚀 Starting SECURITY evaluation run on dataset: '{dataset_to_run}'")
    
    evaluate(
        generate_and_evaluate,
        data=dataset_to_run,
        evaluators=[evaluate_security],
        experiment_prefix="Security_Audit",
        metadata={"model": "claude-3-haiku-20240307", "eval_type": "security_check"}
    )
    
    print("\n✅ Security Evaluation complete.")
