import os
import argparse
from langsmith import evaluate
from test_case_service import TestCaseService
from langsmith_eval import LangSmithEvalService
from dotenv import load_dotenv

load_dotenv()

def generate_and_evaluate(inputs: dict) -> dict:
    """
    This is the target function that LangSmith will execute for each example in the dataset.
    It takes the input (summary, description), generates test cases using our service,
    and returns them.
    """
    summary = inputs.get("summary")
    description = inputs.get("description")
    
    # Initialize our generator service
    tc_service = TestCaseService()
    
    # Generate the test cases using Claude
    result = tc_service.generate_from_text(summary, description)
    
    if result["success"]:
        return {"generated_test_cases": result["test_cases"]}
    else:
        return {"generated_test_cases": f"Generation Failed: {result.get('message')}"}

def evaluate_completeness(run, example) -> dict:
    """Custom Evaluator: Scores completeness."""
    eval_service = LangSmithEvalService()
    
    original_story = f"Summary: {example.inputs['summary']}\nDescription: {example.inputs['description']}"
    generated = run.outputs["generated_test_cases"]
    
    result = eval_service.evaluate_generation(original_story, generated)
    
    if result["success"]:
         # We're parsing the LLM judge output simply. Ideally, we just return the raw text
         # or extract the scores. For now, we'll return the full text as a string value
         return {"key": "LLM_Judge_Review", "score": 1, "comment": result["evaluation"]}
    else:
         return {"key": "LLM_Judge_Review", "score": 0, "comment": "Failed"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Test Case Generation against a LangSmith Dataset.")
    parser.add_argument("--dataset", required=True, help="The exact name of the dataset in LangSmith to run against.")
    args = parser.parse_args()

    print(f"Starting evaluation run on dataset: '{args.dataset}'")
    
    # Run the evaluation
    experiment_results = evaluate(
        generate_and_evaluate,      # The function that generates the output
        data=args.dataset,          # The dataset to evaluate against
        evaluators=[evaluate_completeness],  # Our custom evaluation logic
        experiment_prefix="TC_Gen_Eval",     # Naming the run in LangSmith
        metadata={"model": "claude-3-haiku-20240307"}
    )
    
    print("\n✅ Evaluation run complete.")
    print("View the detailed matrix and scores in your LangSmith dashboard.")
