import logging
from datetime import datetime, timedelta
from ..integrations.slack_integration import SlackIntegration
from ..integrations.github_integration import GitHubIntegration

logger = logging.getLogger(__name__)

class ActivityMonitor:
    """
    Monitors user activity across different platforms.
    Detects decreased activity and provides insights for support.
    """
    
    def __init__(self):
        """Initialize the activity monitor"""
        self.slack = SlackIntegration()
        self.github = GitHubIntegration()
        
        # Store activity history for comparison
        self.activity_history = {}
    
    def check_user_activity(self, user_id, github_username=None):
        """
        Check a user's activity across platforms and detect if it has decreased.
        Returns a dict with activity status and metrics.
        """
        try:
            # Get current timestamp
            now = datetime.now()
            
            # Get Slack activity
            slack_activity = self.slack.get_user_activity(user_id, days=1)
            
            # Get GitHub activity if username is provided
            github_activity = None
            if github_username:
                github_activity = self.github.get_user_activity(github_username, days=1)
            
            # Combine activity metrics
            activity = {
                'timestamp': now,
                'slack': slack_activity,
                'github': github_activity,
                'decreased': False,
                'metrics': {}
            }
            
            # Calculate metrics
            if slack_activity:
                activity['metrics']['slack_messages'] = slack_activity.get('message_count', 0)
                activity['metrics']['slack_channels_active'] = slack_activity.get('channels_active', 0)
            
            if github_activity:
                activity['metrics']['github_commits'] = github_activity.get('commit_count', 0)
                activity['metrics']['github_issues'] = github_activity.get('issue_count', 0)
                activity['metrics']['github_prs'] = github_activity.get('pr_count', 0)
            
            # Check if activity has decreased compared to previous
            if user_id in self.activity_history:
                previous = self.activity_history[user_id]
                
                # Only compare if previous record is from a different day
                prev_date = previous['timestamp'].date()
                current_date = now.date()
                
                if prev_date < current_date:
                    # Compare Slack metrics
                    if slack_activity and 'slack' in previous:
                        prev_slack = previous['metrics'].get('slack_messages', 0)
                        curr_slack = activity['metrics'].get('slack_messages', 0)
                        
                        if curr_slack < prev_slack * 0.7:  # 30% decrease
                            activity['decreased'] = True
                            activity['decrease_reason'] = 'Slack activity has decreased significantly'
                    
                    # Compare GitHub metrics
                    if github_activity and 'github' in previous:
                        prev_github = (
                            previous['metrics'].get('github_commits', 0) +
                            previous['metrics'].get('github_issues', 0) +
                            previous['metrics'].get('github_prs', 0)
                        )
                        curr_github = (
                            activity['metrics'].get('github_commits', 0) +
                            activity['metrics'].get('github_issues', 0) +
                            activity['metrics'].get('github_prs', 0)
                        )
                        
                        if curr_github < prev_github * 0.7:  # 30% decrease
                            activity['decreased'] = True
                            activity['decrease_reason'] = 'GitHub activity has decreased significantly'
            
            # Store current activity for future comparison
            self.activity_history[user_id] = activity
            
            return activity
            
        except Exception as e:
            logger.error(f"Error checking user activity: {e}")
            return {'decreased': False, 'error': str(e)}
    
    def get_activity_trend(self, user_id, days=7):
        """Get activity trend over a period of days"""
        try:
            # This would analyze stored activity data
            # For now, return a placeholder response
            return {
                'user_id': user_id,
                'days_analyzed': days,
                'trend': 'stable',  # Could be 'increasing', 'decreasing', or 'stable'
                'message': f"Activity trend for the past {days} days appears stable."
            }
            
        except Exception as e:
            logger.error(f"Error getting activity trend: {e}")
            return {'error': str(e)}
    
    def get_inactivity_reasons(self, user_id):
        """
        Analyze potential reasons for decreased activity.
        This could include calendar events, holidays, etc.
        """
        try:
            # This would connect to calendar and other data sources
            # For now, return placeholder reasons
            reasons = [
                "User may be in meetings (check calendar)",
                "User might be working on deep focus tasks",
                "Today might be a company holiday or PTO day",
                "User could be working on tasks not tracked in monitored systems"
            ]
            
            return {
                'user_id': user_id,
                'potential_reasons': reasons,
                'message': "Here are some potential reasons for decreased activity."
            }
            
        except Exception as e:
            logger.error(f"Error analyzing inactivity reasons: {e}")
            return {'error': str(e)}
    
    def suggest_support_actions(self, user_id, activity_data):
        """Suggest appropriate support actions based on activity data"""
        try:
            suggestions = []
            
            # Check if activity has decreased
            if activity_data.get('decreased', False):
                # Add general suggestions
                suggestions.append({
                    'type': 'check_in',
                    'message': "Send a friendly check-in message to see if they need assistance."
                })
                
                # Add specific suggestions based on the platform
                if 'decrease_reason' in activity_data:
                    if 'GitHub' in activity_data['decrease_reason']:
                        suggestions.append({
                            'type': 'technical_help',
                            'message': "Offer technical assistance with their current coding tasks."
                        })
                        suggestions.append({
                            'type': 'task_decomposition',
                            'message': "Suggest breaking down complex tasks into smaller, more manageable pieces."
                        })
                    
                    if 'Slack' in activity_data['decrease_reason']:
                        suggestions.append({
                            'type': 'communication_help',
                            'message': "Offer help with drafting messages or preparing for meetings."
                        })
                        suggestions.append({
                            'type': 'motivation',
                            'message': "Provide motivational support and encouragement."
                        })
            
            return {
                'user_id': user_id,
                'suggestions': suggestions
            }
            
        except Exception as e:
            logger.error(f"Error suggesting support actions: {e}")
            return {'error': str(e)}
