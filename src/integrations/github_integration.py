import os
import logging
from github import Github
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """
    Handles integration with the GitHub API.
    Provides methods for monitoring activity, managing issues, and accessing repositories.
    """
    
    def __init__(self):
        """Initialize the GitHub integration with API token"""
        self.github = Github(os.environ.get("GITHUB_TOKEN"))
    
    def get_user_activity(self, username, days=1):
        """Get a user's activity on GitHub over a period of time"""
        try:
            # Get the user
            user = self.github.get_user(username)
            
            # Calculate the time period
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Get the user's events
            events = user.get_events()
            
            # Filter events by time
            recent_events = [
                event for event in events
                if event.created_at >= start_time and event.created_at <= end_time
            ]
            
            # Count different types of activity
            activity = {
                "total_events": len(recent_events),
                "commit_count": 0,
                "issue_count": 0,
                "pr_count": 0,
                "comment_count": 0,
                "repositories": set(),
                "last_active": None
            }
            
            for event in recent_events:
                # Update last active time if newer
                if not activity["last_active"] or event.created_at > activity["last_active"]:
                    activity["last_active"] = event.created_at
                
                # Count by event type
                if event.type == "PushEvent":
                    activity["commit_count"] += len(event.payload.get("commits", []))
                    activity["repositories"].add(event.repo.name)
                elif event.type == "IssuesEvent":
                    activity["issue_count"] += 1
                    activity["repositories"].add(event.repo.name)
                elif event.type == "PullRequestEvent":
                    activity["pr_count"] += 1
                    activity["repositories"].add(event.repo.name)
                elif event.type in ["IssueCommentEvent", "PullRequestReviewCommentEvent", "CommitCommentEvent"]:
                    activity["comment_count"] += 1
                    activity["repositories"].add(event.repo.name)
            
            # Convert repositories set to count
            activity["repository_count"] = len(activity["repositories"])
            activity["repositories"] = list(activity["repositories"])
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting GitHub activity for {username}: {e}")
            return None
    
    def get_user_issues(self, username):
        """Get open issues assigned to a user"""
        try:
            # Search for issues assigned to the user
            query = f"assignee:{username} is:open"
            issues = self.github.search_issues(query)
            
            # Format the issues
            formatted_issues = []
            for issue in issues:
                formatted_issues.append({
                    "id": issue.number,
                    "title": issue.title,
                    "repository": issue.repository.full_name,
                    "url": issue.html_url,
                    "created_at": issue.created_at,
                    "updated_at": issue.updated_at,
                    "labels": [label.name for label in issue.labels]
                })
            
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error getting GitHub issues for {username}: {e}")
            return []
    
    def get_user_pull_requests(self, username):
        """Get open pull requests created by a user"""
        try:
            # Search for pull requests created by the user
            query = f"author:{username} is:pr is:open"
            prs = self.github.search_issues(query)
            
            # Format the pull requests
            formatted_prs = []
            for pr in prs:
                formatted_prs.append({
                    "id": pr.number,
                    "title": pr.title,
                    "repository": pr.repository.full_name,
                    "url": pr.html_url,
                    "created_at": pr.created_at,
                    "updated_at": pr.updated_at,
                    "labels": [label.name for label in pr.labels]
                })
            
            return formatted_prs
            
        except Exception as e:
            logger.error(f"Error getting GitHub PRs for {username}: {e}")
            return []
    
    def create_issue(self, repository_name, title, body, labels=None, assignees=None):
        """Create a new issue in a repository"""
        try:
            # Get the repository
            repo = self.github.get_repo(repository_name)
            
            # Create the issue
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            
            return {
                "success": True,
                "issue_number": issue.number,
                "url": issue.html_url
            }
            
        except Exception as e:
            logger.error(f"Error creating GitHub issue in {repository_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_pull_request(self, repository_name, title, body, head, base="main"):
        """Create a new pull request in a repository"""
        try:
            # Get the repository
            repo = self.github.get_repo(repository_name)
            
            # Create the pull request
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            return {
                "success": True,
                "pr_number": pr.number,
                "url": pr.html_url
            }
            
        except Exception as e:
            logger.error(f"Error creating GitHub PR in {repository_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_repository_activity(self, repository_name, days=7):
        """Get activity in a repository over a period of time"""
        try:
            # Get the repository
            repo = self.github.get_repo(repository_name)
            
            # Calculate the time period
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Get recent commits
            commits = repo.get_commits(since=start_time)
            
            # Get recent issues
            issues = repo.get_issues(state="all", since=start_time)
            
            # Get recent pull requests (via issues API with is:pr filter)
            pulls = [issue for issue in issues if issue.pull_request]
            
            # Count activity
            activity = {
                "commit_count": commits.totalCount,
                "issue_count": len([i for i in issues if not i.pull_request]),
                "pr_count": len(pulls),
                "contributor_count": len(set(c.author.login for c in commits if c.author))
            }
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting repository activity for {repository_name}: {e}")
            return None
    
    def compare_activity(self, username, current_days=1, previous_days=1):
        """Compare a user's recent activity with their previous activity"""
        try:
            # Get current activity
            current_activity = self.get_user_activity(username, days=current_days)
            
            # Get previous activity
            end_time = datetime.now() - timedelta(days=current_days)
            start_time = end_time - timedelta(days=previous_days)
            
            # Get the user
            user = self.github.get_user(username)
            
            # Get the user's events
            events = user.get_events()
            
            # Filter events by time
            previous_events = [
                event for event in events
                if event.created_at >= start_time and event.created_at <= end_time
            ]
            
            # Count different types of activity
            previous_activity = {
                "total_events": len(previous_events),
                "commit_count": 0,
                "issue_count": 0,
                "pr_count": 0,
                "comment_count": 0,
                "repositories": set(),
                "last_active": None
            }
            
            for event in previous_events:
                # Update last active time if newer
                if not previous_activity["last_active"] or event.created_at > previous_activity["last_active"]:
                    previous_activity["last_active"] = event.created_at
                
                # Count by event type
                if event.type == "PushEvent":
                    previous_activity["commit_count"] += len(event.payload.get("commits", []))
                    previous_activity["repositories"].add(event.repo.name)
                elif event.type == "IssuesEvent":
                    previous_activity["issue_count"] += 1
                    previous_activity["repositories"].add(event.repo.name)
                elif event.type == "PullRequestEvent":
                    previous_activity["pr_count"] += 1
                    previous_activity["repositories"].add(event.repo.name)
                elif event.type in ["IssueCommentEvent", "PullRequestReviewCommentEvent", "CommitCommentEvent"]:
                    previous_activity["comment_count"] += 1
                    previous_activity["repositories"].add(event.repo.name)
            
            # Convert repositories set to count
            previous_activity["repository_count"] = len(previous_activity["repositories"])
            previous_activity["repositories"] = list(previous_activity["repositories"])
            
            # Compare activities
            comparison = {
                "total_events_change": current_activity["total_events"] - previous_activity["total_events"],
                "commit_count_change": current_activity["commit_count"] - previous_activity["commit_count"],
                "issue_count_change": current_activity["issue_count"] - previous_activity["issue_count"],
                "pr_count_change": current_activity["pr_count"] - previous_activity["pr_count"],
                "comment_count_change": current_activity["comment_count"] - previous_activity["comment_count"],
                "repository_count_change": current_activity["repository_count"] - previous_activity["repository_count"],
                "decreased": (current_activity["total_events"] < previous_activity["total_events"])
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing GitHub activity for {username}: {e}")
            return None
