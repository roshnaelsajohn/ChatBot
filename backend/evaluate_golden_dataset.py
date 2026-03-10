import os
import argparse
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

def evaluate_against_golden(run, example) -> dict:
    """Evaluator that compares the LLM generation against the Golden Reference."""
    
    generated = run.outputs["generated_test_cases"]
    golden = example.outputs["golden_test_cases"]
    
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
         return {"key": "Golden_Match_Score", "score": 0, "comment": "No Auth Key"}
         
    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",
        temperature=0,
        max_tokens=1024,
        api_key=anthropic_key
    )

    eval_prompt = PromptTemplate.from_template(
        """
        You are an expert QA Manager. Your job is to grade AI-generated test cases against 
        a PERFECT "Golden" reference of Test Cases.
        
        GOLDEN REFERENCE TEST CASES:
        {golden}
        
        AI-GENERATED TEST CASES:
        {generated}
        
        Evaluate the AI-generated test cases solely on how well they cover the scenarios listed in the 
        Golden Reference. It is okay if the AI generated *more* tests, but it MUST cover the basics 
        defined in the Golden Reference.
        
        Score from 1 to 10 (10 meaning all golden scenarios are fully present and tested correctly).
        
        Format your response exactly like this:
        SCORE: [1-10]
        REASON: [1 sentence explanation]
        """
    )
    
    chain = eval_prompt | llm
    
    try:
         result = chain.invoke({
             "golden": golden,
             "generated": generated
         })
         
         # Parse output string (e.g. "SCORE: 8\nREASON: Missed one edge case.")
         content = result.content
         score = 0
         
         import re
         # Search for SCORE: followed by digits
         match = re.search(r"SCORE:\s*(\d+)", content)
         if match:
             try:
                 score_val = int(match.group(1))
                 score = score_val / 10.0 # Langsmith likes scores 0.0 - 1.0
             except:
                 score = 0
                 
         return {"key": "Golden_Match_Score", "score": score, "comment": content}
    except Exception as e:
         return {"key": "Golden_Match_Score", "score": 0, "comment": f"Eval failed: {e}"}

def evaluate_has_edge_cases_section(run, example) -> dict:
    """A Custom Evaluator that checks if the exact string 'Edge Cases' is in the output."""
    
    generated_text = run.outputs["generated_test_cases"]
    
    generated_text = run.outputs["generated_test_cases"].lower()
    
    if "edge case" in generated_text:
        score = 1
        comment = "Output contains reference to Edge Cases."
    else:
        score = 0
        comment = "Missing 'Edge Case' reference in generated output."
        
    return {"key": "Has_Edge_Cases", "score": score, "comment": comment}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Name of Golden Dataset in LangSmith")
    args = parser.parse_args()

    print(f"Starting GOLDEN evaluation run on dataset: '{args.dataset}'")
    
    experiment_results = evaluate(
        generate_and_evaluate,
        data=args.dataset,
        evaluators=[evaluate_against_golden, evaluate_has_edge_cases_section],
        experiment_prefix="Golden_Eval",
        metadata={"model": "claude-3-haiku-20240307", "eval_type": "golden_reference"}
    )
    
    print("\n✅ Golden Evaluation run complete.")
