import logging
from datetime import datetime
from ..integrations.supabase_integration import SupabaseIntegration

logger = logging.getLogger(__name__)

class UserManager:
    """
    Manages user data, preferences, and mappings between different platforms.
    Stores user information for personalized interactions using Supabase.
    """
    
    def __init__(self):
        """Initialize the user manager with Supabase integration"""
        self.supabase = SupabaseIntegration()
        self.user_cache = {}
    
    def get_user(self, slack_id):
        """Get user data by Slack ID"""
        # Check cache first
        if slack_id in self.user_cache:
            return self.user_cache[slack_id]
        
        # Get from Supabase
        user_data = self.supabase.get_user(slack_id)
        
        # Cache the result
        if user_data:
            self.user_cache[slack_id] = user_data
        
        return user_data or {}
    
    def update_user(self, slack_id, data):
        """Update user data"""
        # Get current user data
        user_data = self.get_user(slack_id)
        
        if not user_data:
            # Create new user
            data['slack_id'] = slack_id
            result = self.supabase.create_user(data)
        else:
            # Update existing user
            result = self.supabase.update_user(slack_id, data)
        
        # Update cache
        if result:
            self.user_cache[slack_id] = result
        
        return result or {}
    
    def get_github_username(self, slack_id):
        """Get GitHub username for a Slack user"""
        user = self.get_user(slack_id)
        return user.get('github_username')
    
    def get_email(self, slack_id):
        """Get email for a Slack user"""
        user = self.get_user(slack_id)
        return user.get('email')
    
    def get_preferences(self, slack_id):
        """Get user preferences"""
        user = self.get_user(slack_id)
        return user.get('preferences', {})
    
    def update_preferences(self, slack_id, preferences):
        """Update user preferences"""
        # Get current preferences
        current_prefs = self.get_preferences(slack_id)
        
        # Update with new preferences
        updated_prefs = {**current_prefs, **preferences}
        
        # Save to Supabase
        return self.update_user(slack_id, {'preferences': updated_prefs})
    
    def log_interaction(self, slack_id, interaction_type, details=None):
        """Log an interaction with a user"""
        # Log interaction directly to Supabase
        return self.supabase.log_interaction(slack_id, interaction_type, details)
    
    def get_recent_interactions(self, slack_id, interaction_type=None, limit=10):
        """Get recent interactions with a user"""
        # Get interactions from Supabase
        return self.supabase.get_recent_interactions(slack_id, interaction_type, limit)
    
    def map_slack_to_github(self, slack_id, github_username):
        """Map a Slack ID to a GitHub username"""
        # Update user in Supabase
        result = self.update_user(slack_id, {'github_username': github_username})
        
        # Store GitHub token in credentials table if available
        user = self.get_user(slack_id)
        if 'github_token' in user:
            self.supabase.store_credentials(slack_id, 'github', {
                'token': user['github_token'],
                'username': github_username
            })
        
        return result
    
    def map_slack_to_email(self, slack_id, email):
        """Map a Slack ID to an email address"""
        return self.update_user(slack_id, {'email': email})
    
    def get_all_users(self):
        """Get all users"""
        return self.supabase.get_all_users()
    
    def get_active_users(self, days=7):
        """Get users active in the last X days"""
        # This would ideally be a Supabase query with a date filter
        # For now, we'll get all users and filter in memory
        all_users = self.get_all_users()
        active_users = []
        
        cutoff = (datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        for user in all_users:
            # Check last interaction from Supabase
            recent_interactions = self.get_recent_interactions(user['slack_id'], limit=1)
            
            if recent_interactions and recent_interactions[0]['created_at'] >= cutoff:
                active_users.append(user)
        
        return active_users
        
    def store_credentials(self, slack_id, credential_type, credentials):
        """Store user credentials in Supabase"""
        return self.supabase.store_credentials(slack_id, credential_type, credentials)
    
    def get_credentials(self, slack_id, credential_type):
        """Get user credentials from Supabase"""
        return self.supabase.get_credentials(slack_id, credential_type)
