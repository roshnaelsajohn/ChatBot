import os
from langsmith import Client
from dotenv import load_dotenv
import datetime

load_dotenv()

# Example User Stories to add to the dataset
USER_STORIES = [
    {
        "input": {
            "summary": "User Login with MFA",
            "description": "As a user, I want to securely log in using Multi-Factor Authentication (MFA) via SMS so that my account is protected.",
        },
        "output": {
            "golden_test_cases": """
# Positive Test Cases
1. Successful Login with Valid Credentials
2. Successful Login with Valid Credentials and MFA
# Negative Test Cases
1. Login with Invalid Password
2. Login with Invalid Username
3. Login with Invalid MFA Code (fails)
4. Login with Expired MFA Code (fails)
# Edge Cases
1. Empty Username/Password fields
2. Resend MFA Code after timeout
            """
        }
    },
    {
        "input": {
            "summary": "Shopping Cart Checkout",
            "description": "As a user, I want to review my items and enter my payment details so I can purchase my items.",
        },
        "output": {
            "golden_test_cases": """
# Positive Test Cases
1. Add Item to Cart Successfully
2. Enter Valid Shipping Address
3. Enter Valid Payment Details (Credit Card)
4. Successful Checkout and Order Confirmation
# Negative Test Cases
1. Proceed with Empty Cart (cannot proceed)
2. Enter Invalid Credit Card Number
3. Enter Expired Credit Card
4. Enter Invalid CVV
5. Leave Mandatory Address Fields Blank
# Edge Cases
1. Credit Card Declined by Bank
2. Payment session timeout
            """
        }
    },
    {
         "input": {
            "summary": "Password Reset functionality",
            "description": "As a user who forgot their password, I want to request a password reset link to my email so I can regain access.",
        },
        "output": {
             "golden_test_cases": """
# Positive Test Cases
1. Request Password Reset for Registered Email (link sent)
2. Click Reset Link -> Enter New Valid Password -> Success
# Negative Test Cases
1. Request Password Reset for Unregistered Email (no error, silent fail)
2. Click Expired Reset Link (error shown)
3. Click Already Used Reset Link (error shown)
4. Enter New Password that Does Not Meet Complexity Rules
# Edge Cases
1. Request multiple reset links in a short time
2. Network disconnection during password submission
             """
        }
    }
]

def create_dataset():
    """Create a LangSmith Dataset and add examples to it."""
    # 1. Initialize LangSmith Client
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        print("Error: LANGSMITH_API_KEY not found in environment variables.")
        return
        
    client = Client(api_key=api_key)
    
    # 2. Define Dataset Name
    dataset_name = f"Jira User Stories - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # 3. Create the Dataset
    print(f"Creating dataset '{dataset_name}'...")
    try:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="A dataset of User Stories to evaluate LLM Test Case Generation.",
        )
        print(f"✅ Dataset created successfully! ID: {dataset.id}")
        
        # 4. Add examples to the Dataset
        print("Adding examples to the dataset...")
        for example in USER_STORIES:
            client.create_example(
                inputs=example["input"],
                outputs=example["output"],
                dataset_id=dataset.id
            )
        print("✅ Added 3 examples to the dataset.")
        print(f"\nYou can now view your dataset at: https://smith.langchain.com")
        print(f"Dataset Name: {dataset_name}")
        
    except Exception as e:
        print(f"❌ Error creating dataset: {e}")

if __name__ == "__main__":
    create_dataset()
