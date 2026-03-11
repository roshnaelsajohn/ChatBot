import os
from langsmith import Client
from dotenv import load_dotenv
import datetime

load_dotenv()

# --- CONFIGURATION ---
# Target Dataset ID in LangSmith (tries .env first, then falls back to hardcoded default)
TARGET_DATASET_ID = os.environ.get("LANGSMITH_TARGET_DATASET_ID", "c884189a-4c1e-4a9e-b565-7dad2b174992")
# ---------------------

# We use the exact template structure the user achieved via RAG as our "Golden Standard"
USER_STORIES = [
    {
        "input": {
            "summary": "Access Dashboard",
            "description": "PROJ-1234: As a user, I want to log in so I can access my dashboard.",
        },
        "output": {
            "golden_test_cases": """
Test Case ID: TC-001

Test Case Title: Verify user login with valid credentials

Jira User Story: PROJ-1234

Acceptance Criteria:
User can login with valid email/password and see the dashboard

Module / Feature: Authentication

Priority: P1 - Critical
Severity: High
Test Type: Functional / Regression
Author: [Test Engineer Name]
Created Date: [DD/MM/YYYY]
Last Updated: [DD/MM/YYYY]
Automation Status: Manual / Automated / To Be Automated

Preconditions:
1. Application is accessible and running on the test environment.
2. Test user account exists with valid credentials.
3. Browser is Chrome v120+ or Firefox v115+.

Test Steps:
1. Navigate to the application URL.
Expected Result: Login page is displayed.
Test Data / Notes: -

2. Enter valid username and password.
Expected Result: Credentials are accepted.
Test Data / Notes: Use test account: testuser@example.com

3. Click the 'Login' button.
Expected Result: User is redirected to dashboard.
Test Data / Notes: -

4. Verify dashboard elements are loaded.
Expected Result: All widgets display correctly.
Test Data / Notes: Check: header, sidebar, main content

5. Click 'Logout' button.
Expected Result: User is logged out and redirected to login page.
Test Data / Notes: Session should be terminated

Post-conditions:
1. User session is active, and the dashboard is loaded.
2. Audit log records the login event.

Executed By: [Tester Name]
Execution Date: [DD/MM/YYYY]
Environment: QA / Staging / UAT / Production
Browser / Device: Chrome 120 / Windows 11
Build Version: [v1.2.3]
Status: Pass / Fail / Blocked / Skipped
Defect ID (if failed): BUG-5678 (linked in Jira)
Comments: [Any observations or notes]
            """
        }
    }
]

def add_to_existing_dataset(dataset_id):
    """Add examples to the specific existing LangSmith Dataset."""
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        print("Error: LANGSMITH_API_KEY not found.")
        return
        
    client = Client(api_key=api_key)
    
    print(f"Adding examples to existing dataset ID: {dataset_id}...")
    try:
        for example in USER_STORIES:
            client.create_example(
                inputs=example["input"],
                outputs=example["output"],
                dataset_id=dataset_id
            )
        print(f"✅ Successfully added examples to dataset {dataset_id}!")
        
    except Exception as e:
        print(f"❌ Error adding to dataset: {e}")

if __name__ == "__main__":
    # --- OPTION A: Add to your specific existing 'TestFly' dataset ---
    # Target Dataset ID: c884189a-4c1e-4a9e-b565-7dad2b174992
    add_to_existing_dataset(TARGET_DATASET_ID)
    
    # --- OPTION B: If you wanted a SEPARATE dataset for a different project ---
    # You would simply change the ID or name and run the code again:
    # add_to_existing_dataset("ANOTHER_DATASET_ID")
