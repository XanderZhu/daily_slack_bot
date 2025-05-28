import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OnboardingManager:
    """
    Manages the onboarding process for new users.
    Handles credential collection and setup for various integrations.
    """
    
    def __init__(self, user_manager):
        """Initialize the onboarding manager"""
        self.user_manager = user_manager
    
    def check_onboarding_status(self, user_id):
        """Check if a user has completed onboarding"""
        user_data = self.user_manager.get_user(user_id)
        return user_data.get("onboarding_completed", False)
    
    def start_onboarding(self, user_id):
        """Start the onboarding process for a user"""
        # Mark that onboarding has started
        self.user_manager.update_user(user_id, {
            "onboarding_started": True,
            "onboarding_step": "welcome",
            "onboarding_timestamp": datetime.now().isoformat()
        })
        
        # Return the welcome message
        return self._get_welcome_message()
    
    def process_onboarding_step(self, user_id, message):
        """Process a user's response during onboarding"""
        user_data = self.user_manager.get_user(user_id)
        current_step = user_data.get("onboarding_step", "welcome")
        
        logger.info(f"Processing onboarding step for user {user_id}: current_step={current_step}, message='{message}'")
        logger.info(f"User data: {user_data}")
        
        if current_step == "welcome":
            # Check if the message is a valid response to continue
            if message.lower() in ["continue", "yes", "ok", "start"]:
                # Move to GitHub credentials step
                logger.info(f"User {user_id} confirmed to continue. Moving to GitHub step.")
                update_result = self.user_manager.update_user(user_id, {"onboarding_step": "github"})
                logger.info(f"Update result: {update_result}")
                return self._get_github_prompt()
            else:
                # If the user didn't type a valid continue command, repeat the welcome message
                logger.info(f"User {user_id} sent invalid continue response: '{message}'")
                return "Please type 'continue' when you're ready to proceed with the setup."
            
        elif current_step == "github":
            # Save GitHub token
            if self._validate_github_token(message):
                self._save_github_credentials(user_id, message)
                # Move to the next step - this is already done in _save_github_credentials for skip case
                if message.lower() not in ["skip", "later", "no"]:
                    self.user_manager.update_user(user_id, {"onboarding_step": "google"})
                    return self._get_google_prompt()
                # If we're here, the _save_github_credentials method already moved to the next step
                return self._get_google_prompt()
            else:
                return "That doesn't appear to be a valid GitHub token. Please provide a valid personal access token."
            
        elif current_step == "google":
            # Save Google credentials
            if message.lower() in ["skip", "later", "no"]:
                self.user_manager.update_user(user_id, {"onboarding_step": "youtrack"})
                return self._get_youtrack_prompt()
            else:
                # For Google, we need to handle the OAuth flow separately
                # For now, just provide instructions
                self.user_manager.update_user(user_id, {"onboarding_step": "youtrack"})
                return ("I'll help you set up Google integration later. You'll need to go through an OAuth flow.\n\n" + 
                        self._get_youtrack_prompt())
            
        elif current_step == "youtrack":
            # Save YouTrack credentials
            if message.lower() in ["skip", "later", "no"]:
                return self._complete_onboarding(user_id)
            else:
                parts = message.strip().split()
                if len(parts) >= 2:
                    url = parts[0]
                    token = parts[1]
                    self._save_youtrack_credentials(user_id, url, token)
                    return self._complete_onboarding(user_id)
                else:
                    return "Please provide both the YouTrack URL and token separated by a space, or type 'skip' to skip this step."
        
        else:
            # Unknown step, reset to welcome
            self.user_manager.update_user(user_id, {"onboarding_step": "welcome"})
            return self._get_welcome_message()
    
    def _get_welcome_message(self):
        """Get the welcome message for onboarding"""
        return (
            "👋 Welcome to the Daily Slack Bot! I'm here to help you stay productive and motivated.\n\n"
            "To provide you with the best experience, I need access to some of your work tools. "
            "Let's set up your integrations.\n\n"
            "I'll guide you through setting up access to:\n"
            "• GitHub - for monitoring coding activity and managing issues\n"
            "• Google services (Calendar & Gmail) - for meetings and emails\n"
            "• YouTrack - for task management\n\n"
            "You can skip any integration you don't want to set up now.\n\n"
            "Let's get started! Type 'continue' when you're ready."
        )
    
    def _get_github_prompt(self):
        """Get the prompt for GitHub credentials"""
        return (
            "First, let's set up GitHub integration.\n\n"
            "Please provide your GitHub personal access token. "
            "You can create one at https://github.com/settings/tokens\n\n"
            "Your token needs these permissions:\n"
            "• repo (Full control of private repositories)\n"
            "• user (Read-only access to user information)\n\n"
            "Type your token or 'skip' to set up later."
        )
    
    def _get_google_prompt(self):
        """Get the prompt for Google credentials"""
        return (
            "Great! Now let's set up Google integration for Calendar and Gmail.\n\n"
            "Setting up Google integration requires a more complex OAuth flow.\n\n"
            "Would you like me to guide you through setting up Google integration now, "
            "or would you prefer to do it later?\n\n"
            "Type 'continue' to set up now or 'skip' to do it later."
        )
    
    def _get_youtrack_prompt(self):
        """Get the prompt for YouTrack credentials"""
        return (
            "Finally, let's set up YouTrack integration for task management.\n\n"
            "Please provide your YouTrack URL and permanent token in this format:\n"
            "`https://youtrack.example.com your-token-here`\n\n"
            "You can create a permanent token in your YouTrack profile settings.\n\n"
            "Type your YouTrack URL and token or 'skip' to set up later."
        )
    
    def _validate_github_token(self, token):
        """Validate a GitHub token (basic validation only)"""
        # Basic validation - GitHub tokens are 40 characters
        token = token.strip()
        if token.lower() in ["skip", "later", "no"]:
            return True
        return len(token) == 40 and token.isalnum()
    
    def _save_github_credentials(self, user_id, token):
        """Save GitHub credentials"""
        if token.lower() in ["skip", "later", "no"]:
            # Update user data to mark GitHub setup as skipped
            self.user_manager.update_user(user_id, {
                "github_setup": "skipped",
                "onboarding_step": "google"  # Move to the next step
            })
            logger.info(f"User {user_id} skipped GitHub setup")
            return
            
        # Save token to user data
        self.user_manager.update_user(user_id, {
            "github_setup": "completed"
        })
        
        # Save token to credentials in SQLite
        github_creds = {
            "token": token,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            self.user_manager.store_credentials(user_id, "github", github_creds)
            logger.info(f"Saved GitHub credentials for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving GitHub credentials for user {user_id}: {e}")
    
    def _save_google_credentials(self, user_id, client_id, client_secret, refresh_token):
        """Save Google credentials"""
        # Update user data to mark Google setup as completed
        self.user_manager.update_user(user_id, {
            "google_setup": "completed"
        })
        
        # Save to credentials in Supabase
        google_creds = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            self.user_manager.store_credentials(user_id, "google", google_creds)
            logger.info(f"Saved Google credentials for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving Google credentials for user {user_id}: {e}")
    
    def _save_youtrack_credentials(self, user_id, url, token):
        """Save YouTrack credentials"""
        # Save to user data
        self.user_manager.update_user(user_id, {
            "youtrack_setup": "completed"
        })
        
        # Save to credentials in Supabase
        youtrack_creds = {
            "url": url,
            "token": token,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            self.user_manager.store_credentials(user_id, "youtrack", youtrack_creds)
            logger.info(f"Saved YouTrack credentials for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving YouTrack credentials for user {user_id}: {e}")
    
    def _handle_google_oauth_flow(self, user_id, message):
        # Handle Google OAuth flow
        # This is a placeholder for now
        client_id = "your_client_id"
        client_secret = "your_client_secret"
        refresh_token = "your_refresh_token"
        return client_id, client_secret, refresh_token
    
    def _complete_onboarding(self, user_id):
        """Complete the onboarding process"""
        self.user_manager.update_user(user_id, {
            "onboarding_completed": True,
            "onboarding_step": "completed",
            "onboarding_completion_timestamp": datetime.now().isoformat()
        })
        
        return (
            "🎉 Thank you! Your onboarding is now complete.\n\n"
            "I'm ready to help you with:\n"
            "• Daily planning and task management\n"
            "• Hourly check-ins to offer assistance\n"
            "• Monitoring your activity and providing support when needed\n"
            "• Helping with research, coding, and communication tasks\n\n"
            "I'll send you a daily welcome message with your meetings and tasks each morning.\n\n"
            "Is there anything specific you'd like help with right now?"
        )
