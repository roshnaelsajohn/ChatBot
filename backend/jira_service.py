import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

class JiraService:
    def __init__(self):
        self.server = os.environ.get("JIRA_URL")
        self.email = os.environ.get("JIRA_USER_EMAIL")
        self.token = os.environ.get("JIRA_API_TOKEN")
        self.jira = None

        if self.server and self.email and self.token:
            try:
                self.jira = JIRA(
                    server=self.server,
                    basic_auth=(self.email, self.token)
                )
                print(f"JiraService initialized for server: {self.server}")
            except Exception as e:
                print(f"Failed to initialize Jira client: {e}")
        else:
            print("Warning: Jira credentials missing in .env")

    def get_user_story_details(self, issue_key: str) -> dict:
        """
        Fetch summary and description of a Jira issue.
        """
        if not self.jira:
            return {
                "success": False,
                "message": "Jira client not configured. Please set JIRA_URL, JIRA_USER_EMAIL, and JIRA_API_TOKEN."
            }

        try:
            issue = self.jira.issue(issue_key)
            summary = issue.fields.summary
            description = issue.fields.description or "No description provided."
            
            return {
                "success": True,
                "key": issue_key,
                "summary": summary,
                "description": description
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching Jira issue {issue_key}: {str(e)}"
            }
