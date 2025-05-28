import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class YouTrackIntegration:
    """
    Handles integration with the YouTrack API.
    Provides methods for managing issues, tasks, and projects.
    """
    
    def __init__(self):
        """Initialize the YouTrack integration with API token"""
        self.base_url = os.environ.get("YOUTRACK_URL")
        self.token = os.environ.get("YOUTRACK_TOKEN")
        
        if not self.base_url or not self.token:
            logger.error("YouTrack URL or token not set in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_user_issues(self, username, state="Open"):
        """Get issues assigned to a user"""
        if not self.base_url or not self.token:
            logger.error("YouTrack configuration incomplete")
            return []
        
        try:
            # Build the API URL
            url = f"{self.base_url}/api/issues"
            
            # Set up the query parameters
            params = {
                "query": f"for: {username} State: {state}",
                "fields": "id,summary,description,created,updated,customFields(name,value(name))"
            }
            
            # Make the API request
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Process the response
            issues = response.json()
            
            # Format the issues
            formatted_issues = []
            for issue in issues:
                # Extract custom fields
                custom_fields = {}
                for field in issue.get('customFields', []):
                    if 'value' in field and field['value'] is not None:
                        custom_fields[field['name']] = field['value'].get('name', '')
                
                formatted_issues.append({
                    'id': issue['id'],
                    'summary': issue['summary'],
                    'description': issue.get('description', ''),
                    'created': issue.get('created'),
                    'updated': issue.get('updated'),
                    'priority': custom_fields.get('Priority', 'Normal'),
                    'type': custom_fields.get('Type', 'Task'),
                    'state': custom_fields.get('State', state)
                })
            
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error getting YouTrack issues for {username}: {e}")
            return []
    
    def create_issue(self, project_id, summary, description=None, assignee=None, custom_fields=None):
        """Create a new issue in YouTrack"""
        if not self.base_url or not self.token:
            logger.error("YouTrack configuration incomplete")
            return None
        
        try:
            # Build the API URL
            url = f"{self.base_url}/api/issues"
            
            # Prepare the request body
            body = {
                "project": {"id": project_id},
                "summary": summary
            }
            
            if description:
                body["description"] = description
            
            # Add custom fields if provided
            if custom_fields:
                body["customFields"] = []
                for name, value in custom_fields.items():
                    body["customFields"].append({
                        "name": name,
                        "value": {"name": value}
                    })
            
            # Make the API request
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            
            # Process the response
            issue = response.json()
            
            # If assignee is provided, update the issue
            if assignee:
                self.update_issue(issue['id'], {'Assignee': assignee})
            
            return {
                'success': True,
                'issue_id': issue['id'],
                'url': f"{self.base_url}/issue/{issue['id']}"
            }
            
        except Exception as e:
            logger.error(f"Error creating YouTrack issue: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_issue(self, issue_id, custom_fields):
        """Update an existing issue in YouTrack"""
        if not self.base_url or not self.token:
            logger.error("YouTrack configuration incomplete")
            return None
        
        try:
            # Build the API URL
            url = f"{self.base_url}/api/issues/{issue_id}"
            
            # Prepare the request body
            body = {"customFields": []}
            
            for name, value in custom_fields.items():
                body["customFields"].append({
                    "name": name,
                    "value": {"name": value}
                })
            
            # Make the API request
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            
            return {
                'success': True,
                'issue_id': issue_id
            }
            
        except Exception as e:
            logger.error(f"Error updating YouTrack issue {issue_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_comment(self, issue_id, text):
        """Add a comment to an issue"""
        if not self.base_url or not self.token:
            logger.error("YouTrack configuration incomplete")
            return None
        
        try:
            # Build the API URL
            url = f"{self.base_url}/api/issues/{issue_id}/comments"
            
            # Prepare the request body
            body = {"text": text}
            
            # Make the API request
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            
            # Process the response
            comment = response.json()
            
            return {
                'success': True,
                'comment_id': comment['id']
            }
            
        except Exception as e:
            logger.error(f"Error adding comment to YouTrack issue {issue_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_projects(self):
        """Get a list of available projects"""
        if not self.base_url or not self.token:
            logger.error("YouTrack configuration incomplete")
            return []
        
        try:
            # Build the API URL
            url = f"{self.base_url}/api/admin/projects"
            
            # Set up the query parameters
            params = {
                "fields": "id,name,shortName,description"
            }
            
            # Make the API request
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Process the response
            projects = response.json()
            
            # Format the projects
            formatted_projects = []
            for project in projects:
                formatted_projects.append({
                    'id': project['id'],
                    'name': project['name'],
                    'short_name': project.get('shortName', ''),
                    'description': project.get('description', '')
                })
            
            return formatted_projects
            
        except Exception as e:
            logger.error(f"Error getting YouTrack projects: {e}")
            return []
    
    def get_issue_history(self, issue_id):
        """Get the history of changes for an issue"""
        if not self.base_url or not self.token:
            logger.error("YouTrack configuration incomplete")
            return []
        
        try:
            # Build the API URL
            url = f"{self.base_url}/api/issues/{issue_id}/activities"
            
            # Set up the query parameters
            params = {
                "fields": "id,timestamp,author(login,name),field(name),added(name),removed(name)"
            }
            
            # Make the API request
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Process the response
            activities = response.json()
            
            # Format the activities
            formatted_activities = []
            for activity in activities:
                # Convert timestamp to datetime
                timestamp = datetime.fromtimestamp(activity['timestamp'] / 1000)
                
                formatted_activities.append({
                    'id': activity['id'],
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'author': activity.get('author', {}).get('name', 'Unknown'),
                    'field': activity.get('field', {}).get('name', ''),
                    'added': activity.get('added', {}).get('name', ''),
                    'removed': activity.get('removed', {}).get('name', '')
                })
            
            return formatted_activities
            
        except Exception as e:
            logger.error(f"Error getting history for YouTrack issue {issue_id}: {e}")
            return []
