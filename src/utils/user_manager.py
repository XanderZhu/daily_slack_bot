import logging
import json
import os
from pathlib import Path
from datetime import datetime
from ..integrations.sqlite_integration import SQLiteIntegration

logger = logging.getLogger(__name__)

class UserManager:
    """
    Manages user data, preferences, and mappings between different platforms.
    Stores user information for personalized interactions using Supabase.
    """
    
    def __init__(self):
        """Initialize the user manager with SQLite integration"""
        # Initialize SQLite database for persistent storage
        self.db = SQLiteIntegration()
        
        # Keep the local file storage for backward compatibility
        self.user_cache = {}
        self.local_storage_path = Path("data/users")
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        self.interactions_path = Path("data/interactions")
        self.interactions_path.mkdir(parents=True, exist_ok=True)
        
        # Load any existing local data into cache
        self._load_local_users()
    
    def _load_local_users(self):
        """Load user data from local storage"""
        try:
            for user_file in self.local_storage_path.glob("*.json"):
                try:
                    with open(user_file, 'r') as f:
                        user_data = json.load(f)
                        if 'slack_id' in user_data:
                            self.user_cache[user_data['slack_id']] = user_data
                except Exception as e:
                    logger.error(f"Error loading local user data from {user_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading local users: {e}")
    
    def _save_local_user(self, user_data):
        """Save user data to local storage"""
        if not user_data or 'slack_id' not in user_data:
            return
            
        try:
            file_path = self.local_storage_path / f"{user_data['slack_id']}.json"
            with open(file_path, 'w') as f:
                json.dump(user_data, f)
        except Exception as e:
            logger.error(f"Error saving local user data: {e}")
    
    def _save_local_interaction(self, slack_id, interaction_type, details=None):
        """Save interaction data to local storage"""
        try:
            interaction_data = {
                "slack_id": slack_id,
                "interaction_type": interaction_type,
                "details": details,
                "created_at": datetime.now().isoformat()
            }
            
            # Create a filename with timestamp to ensure uniqueness
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            file_path = self.interactions_path / f"{slack_id}_{timestamp}.json"
            
            with open(file_path, 'w') as f:
                json.dump(interaction_data, f)
                
            return interaction_data
        except Exception as e:
            logger.error(f"Error saving local interaction data: {e}")
            return None
    
    def get_user(self, slack_id):
        """Get user data by Slack ID"""
        # Check cache first
        if slack_id in self.user_cache:
            return self.user_cache[slack_id]
        
        # Try to get from SQLite database
        user_data = None
        if self.db:
            user_data = self.db.get_user(slack_id)
        
        # If not in database, check local storage (for backward compatibility)
        if not user_data:
            file_path = self.local_storage_path / f"{slack_id}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        user_data = json.load(f)
                        # If found in local storage, migrate to SQLite
                        if user_data and self.db:
                            self.db.create_user(user_data)
                except Exception as e:
                    logger.error(f"Error reading local user data: {e}")
        
        # Cache the result
        if user_data:
            self.user_cache[slack_id] = user_data
        
        return user_data or {}
    
    def update_user(self, slack_id, data):
        """Update user data"""
        # Get current user data
        user_data = self.get_user(slack_id)
        result = None
        
        # Try to update in SQLite database if available
        if self.db:
            # Merge the new data with existing data
            if user_data:
                merged_data = {**user_data, **data}
                result = self.db.update_user(slack_id, merged_data)
            else:
                # Create new user if it doesn't exist
                new_user = {**data, 'slack_id': slack_id}
                if 'created_at' not in new_user:
                    new_user['created_at'] = datetime.now().isoformat()
                result = self.db.create_user(new_user)
        
        # If database failed or not available, use local storage
        if not result:
            if not user_data:
                # New user
                data['slack_id'] = slack_id
                if 'created_at' not in data:
                    data['created_at'] = datetime.now().isoformat()
                result = data
            else:
                # Update existing user
                result = {**user_data, **data}
                result['updated_at'] = datetime.now().isoformat()
            
            # Save to local storage
            self._save_local_user(result)
        
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
        
        # Save to SQLite
        return self.update_user(slack_id, {'preferences': updated_prefs})
    
    def log_interaction(self, slack_id, interaction_type, details=None):
        """Log an interaction with a user"""
        result = None
        
        # Try to log in SQLite database if available
        if self.db:
            result = self.db.log_interaction(slack_id, interaction_type, details)
        
        # If database failed or not available, log locally
        if not result:
            result = self._save_local_interaction(slack_id, interaction_type, details)
        
        return result
    
    def get_recent_interactions(self, slack_id, interaction_type=None, limit=10):
        """Get recent interactions with a user"""
        interactions = []
        
        # Try to get from SQLite database if available
        if self.db:
            interactions = self.db.get_recent_interactions(slack_id, interaction_type, limit)
        
        # If Supabase failed or not available, use local storage
        if not interactions:
            try:
                # Get all interaction files for this user
                user_interactions = list(self.interactions_path.glob(f"{slack_id}_*.json"))
                
                # Load each interaction
                loaded_interactions = []
                for file_path in user_interactions:
                    try:
                        with open(file_path, 'r') as f:
                            interaction = json.load(f)
                            if interaction_type is None or interaction.get('interaction_type') == interaction_type:
                                loaded_interactions.append(interaction)
                    except Exception as e:
                        logger.error(f"Error loading interaction from {file_path}: {e}")
                
                # Sort by created_at (newest first) and limit
                loaded_interactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                interactions = loaded_interactions[:limit]
            except Exception as e:
                logger.error(f"Error getting local interactions: {e}")
        
        return interactions
    
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
        users = []
        
        # Try to get from SQLite database if available
        if self.db:
            users = self.db.get_all_users()
        
        # If Supabase failed or not available, use local storage
        if not users:
            try:
                # Get all user files
                for user_file in self.local_storage_path.glob("*.json"):
                    try:
                        with open(user_file, 'r') as f:
                            user_data = json.load(f)
                            users.append(user_data)
                    except Exception as e:
                        logger.error(f"Error loading user from {user_file}: {e}")
            except Exception as e:
                logger.error(f"Error getting local users: {e}")
        
        return users
    
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
        """Store user credentials in database"""
        result = None
        
        # Try to store in SQLite database if available
        if self.db:
            result = self.db.store_credentials(slack_id, credential_type, credentials)
        
        # If Supabase failed or not available, store in user data
        if not result:
            try:
                # Get current user data
                user_data = self.get_user(slack_id) or {'slack_id': slack_id}
                
                # Add credentials to user data
                if 'credentials' not in user_data:
                    user_data['credentials'] = {}
                user_data['credentials'][credential_type] = credentials
                
                # Update user
                self.update_user(slack_id, user_data)
                result = {'slack_id': slack_id, 'credential_type': credential_type, 'data': credentials}
            except Exception as e:
                logger.error(f"Error storing credentials locally: {e}")
        
        return result
    
    def get_credentials(self, slack_id, credential_type):
        """Get user credentials from database"""
        credentials = None
        
        # Try to get from SQLite database if available
        if self.db:
            credentials_data = self.db.get_credentials(slack_id, credential_type)
            if credentials_data:
                return credentials_data
        
        # If Supabase failed or not available, get from user data
        try:
            user_data = self.get_user(slack_id)
            if user_data and 'credentials' in user_data and credential_type in user_data['credentials']:
                credentials = user_data['credentials'][credential_type]
        except Exception as e:
            logger.error(f"Error getting credentials locally: {e}")
        
        return credentials
