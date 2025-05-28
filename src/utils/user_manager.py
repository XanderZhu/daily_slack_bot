import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class UserManager:
    """
    Manages user data, preferences, and mappings between different platforms.
    Stores user information for personalized interactions.
    """
    
    def __init__(self, data_dir="data"):
        """Initialize the user manager"""
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.users = self._load_users()
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def _load_users(self):
        """Load user data from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading user data: {e}")
                return {}
        else:
            return {}
    
    def _save_users(self):
        """Save user data to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
    
    def get_user(self, slack_id):
        """Get user data by Slack ID"""
        return self.users.get(slack_id, {})
    
    def update_user(self, slack_id, data):
        """Update user data"""
        if slack_id not in self.users:
            self.users[slack_id] = {}
        
        self.users[slack_id].update(data)
        self.users[slack_id]['last_updated'] = datetime.now().isoformat()
        
        self._save_users()
        return self.users[slack_id]
    
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
        user = self.get_user(slack_id)
        
        if 'preferences' not in user:
            user['preferences'] = {}
        
        user['preferences'].update(preferences)
        
        return self.update_user(slack_id, user)
    
    def log_interaction(self, slack_id, interaction_type, details=None):
        """Log an interaction with a user"""
        user = self.get_user(slack_id)
        
        if 'interactions' not in user:
            user['interactions'] = []
        
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type
        }
        
        if details:
            interaction['details'] = details
        
        user['interactions'].append(interaction)
        
        # Keep only the last 100 interactions
        if len(user['interactions']) > 100:
            user['interactions'] = user['interactions'][-100:]
        
        return self.update_user(slack_id, user)
    
    def get_recent_interactions(self, slack_id, interaction_type=None, limit=10):
        """Get recent interactions with a user"""
        user = self.get_user(slack_id)
        interactions = user.get('interactions', [])
        
        # Filter by type if specified
        if interaction_type:
            interactions = [i for i in interactions if i['type'] == interaction_type]
        
        # Sort by timestamp (newest first) and limit
        interactions.sort(key=lambda x: x['timestamp'], reverse=True)
        return interactions[:limit]
    
    def map_slack_to_github(self, slack_id, github_username):
        """Map a Slack ID to a GitHub username"""
        return self.update_user(slack_id, {'github_username': github_username})
    
    def map_slack_to_email(self, slack_id, email):
        """Map a Slack ID to an email address"""
        return self.update_user(slack_id, {'email': email})
    
    def get_all_users(self):
        """Get all users"""
        return self.users
    
    def get_active_users(self, days=7):
        """Get users active in the last X days"""
        active_users = {}
        cutoff = (datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        for slack_id, user in self.users.items():
            # Check last interaction
            interactions = user.get('interactions', [])
            if interactions:
                latest = max(interactions, key=lambda x: x['timestamp'])
                if latest['timestamp'] >= cutoff:
                    active_users[slack_id] = user
        
        return active_users
