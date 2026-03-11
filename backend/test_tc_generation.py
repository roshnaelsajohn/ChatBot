import json
from test_case_service import TestCaseService
from langsmith_eval import LangSmithEvalService
from dotenv import load_dotenv

load_dotenv()

def run_test():
    tc_service = TestCaseService()
    eval_service = LangSmithEvalService()
    
    summary = "User Login with MFA"
    description = "As a user, I want to securely log in using Multi-Factor Authentication (MFA) via SMS so that my account is protected."
    
    print("1. Generating Test Cases...")
    tc_result = tc_service.generate_from_text(summary, description)
    
    if not tc_result["success"]:
        print("Generation failed:", tc_result.get("message"))
        return
        
    generated_tests = tc_result["test_cases"]
    print("Generation successful. First 200 chars:")
    print(generated_tests[:200] + "...\n")
    
    original_story = f"Summary: {summary}\nDescription: {description}"
    
    print("2. Evaluating Generated Test Cases...")
    eval_result = eval_service.evaluate_generation(original_story, generated_tests)
    
    if not eval_result["success"]:
        print("Evaluation failed:", eval_result.get("message"))
        return
        
    print("Evaluation successful:")
    print(eval_result["evaluation"])

if __name__ == "__main__":
    run_test()
