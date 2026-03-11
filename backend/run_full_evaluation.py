import os
import argparse
from create_ls_dataset_template import create_fresh_dataset
from evaluate_golden_dataset import run_golden_evaluation

def main():
    parser = argparse.ArgumentParser(description="One-click Fresh Test Run: Creates a new dataset and evaluates it.")
    parser.add_argument("--name", help="Optional prefix for the dataset name")
    args = parser.parse_args()

    print("🚀 Starting a Fresh Integrated Test Run...")
    
    # 1. Create a brand new dataset for this specific run
    new_dataset_name, new_dataset_id = create_fresh_dataset()
    
    if not new_dataset_name:
        print("❌ Failed to create a fresh dataset. Aborting run.")
        return

    # Print the direct link to the dataset itself
    org_id = "e922535e-c0cd-4a12-837d-6893d7933f98" # Based on your URLs
    dataset_url = f"https://smith.langchain.com/o/{org_id}/datasets/{new_dataset_id}"
    print(f"📂 View Dataset: {dataset_url}")

    # 2. Immediately run the evaluation against this new dataset
    print(f"\n🧪 Triggering evaluation for '{new_dataset_name}'...")
    run_golden_evaluation(new_dataset_name)

    print("\n✅ Integrated Run Complete!")
    print(f"Check LangSmith for the dataset and experiment named similarly to: {new_dataset_name}")

if __name__ == "__main__":
    main()
