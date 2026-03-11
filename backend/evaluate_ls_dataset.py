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

import re

def evaluate_metrics(run, example) -> dict:
    """
    Evaluator that parses the LLM-as-a-judge response into separate scores.
    """
    eval_service = LangSmithEvalService()
    
    original_story = f"Summary: {example.inputs['summary']}\nDescription: {example.inputs['description']}"
    generated = run.outputs["generated_test_cases"]
    
    result = eval_service.evaluate_generation(original_story, generated)
    
    if not result["success"]:
        return [{"key": "LLM_Eval_Error", "score": 0, "comment": result.get("message")}]
    
    feedback = result["evaluation"]
    
    # Parse scores using regex
    # Looking for formats like "Completeness: 8/10" or "Clarity: 9"
    metrics = {
        "Completeness": 0,
        "Clarity": 0,
        "Edge Cases": 0
    }
    
    results = []
    for metric in metrics.keys():
        match = re.search(rf"{metric}:\s*(\d+)", feedback, re.IGNORECASE)
        if match:
            score_val = int(match.group(1))
            normalized_score = score_val / 10.0
            results.append({"key": metric.replace(" ", "_"), "score": normalized_score})
            
    # Add the full feedback as a comment on the first metric
    if results:
        results[0]["comment"] = feedback
    else:
        results.append({"key": "Eval_Parsing_Failed", "score": 0, "comment": feedback})
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Test Case Generation against a LangSmith Dataset.")
    parser.add_argument("--dataset", help="The exact name or ID of the dataset in LangSmith.")
    args = parser.parse_args()

    # Priority: 1. Arg, 2. Env
    dataset_to_run = args.dataset or os.environ.get("LANGSMITH_TARGET_DATASET_ID")

    if not dataset_to_run:
        print("❌ Error: No dataset provided via --dataset and LANGSMITH_TARGET_DATASET_ID not set in .env")
    else:
        print(f"Starting Quality evaluation run on dataset: '{dataset_to_run}'")
        
        # Run the evaluation
        experiment_results = evaluate(
            generate_and_evaluate,
            data=dataset_to_run,
            evaluators=[evaluate_metrics],
            experiment_prefix="Quality_Matrix",
            metadata={"model": "claude-3-haiku-20240307", "eval_type": "general_quality"}
        )
    
    print("\n✅ Quality Evaluation run complete.")
    print("View the detailed matrix and scores in your LangSmith dashboard.")
