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
        self.mock_agenda = {
            "meetings": [
                {"time": "10:00 AM", "title": "Team Standup"},
                {"time": "2:00 PM", "title": "Product Review"},
            ],
            "tasks": [
                "Implement new feature X",
                "Review pull requests",
                "Update documentation"
            ]
        }
        self.mock_issues = [
            "spending too much time in meetings",
            "context switching between tasks",
            "difficulty prioritizing work"
        ]
    
    def check_onboarding_status(self, user_id):
        """Check if a user has completed onboarding"""
        user_data = self.user_manager.get_user(user_id)
        return user_data.get("onboarding_completed", False)
    
    def start_onboarding(self, user_id):
        """Start the onboarding process for a user"""
        # Mark that onboarding has started
        try:
            # First make sure the user exists
            user_data = self.user_manager.get_user(user_id)
            if not user_data:
                # Create the user if they don't exist
                self.user_manager.update_user(user_id, {
                    "slack_id": user_id,
                    "created_at": datetime.now().isoformat()
                })
            
            # Now update the onboarding fields
            update_result = self.user_manager.update_user(user_id, {
                "onboarding_started": True,
                "onboarding_step": "demo_welcome",  # Start with demo welcome step
                "onboarding_timestamp": datetime.now().isoformat()
            })
            logger.info(f"Start onboarding update result: {update_result}")
            
            # Verify the update worked
            updated_user = self.user_manager.get_user(user_id)
            logger.info(f"User data after starting onboarding: {updated_user}")
        except Exception as e:
            logger.error(f"Error starting onboarding for user {user_id}: {e}")
        
        # Return the welcome message for demo
        return (
            "👋 Welcome to the Daily Slack Bot Demo!\n\n"
            "I'm here to help you stay productive and motivated.\n"
            "For this demo, you can either:\n"
            "• Enter your credentials for full setup\n"
            "• Type 'skip' to see a demo with mock data\n\n"
            "What would you like to do?"
        )
    
    def process_onboarding_step(self, user_id, message):
        """Process a user's response during onboarding"""
        # Force refresh user data from database
        try:
            # Clear cache to ensure fresh data
            if hasattr(self.user_manager, 'user_cache') and user_id in self.user_manager.user_cache:
                del self.user_manager.user_cache[user_id]
                
            user_data = self.user_manager.get_user(user_id)
            
            # If user data is missing or incomplete, try to fix it
            if not user_data or not user_data.get("onboarding_step"):
                logger.warning(f"User {user_id} has incomplete data, attempting to fix")
                # Re-initialize the user with demo_welcome step
                self.user_manager.update_user(user_id, {
                    "slack_id": user_id,
                    "onboarding_started": True,
                    "onboarding_step": "demo_welcome",
                    "onboarding_timestamp": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat() if not user_data else user_data.get("created_at")
                })
                # Get fresh data
                user_data = self.user_manager.get_user(user_id)
            
            current_step = user_data.get("onboarding_step", "demo_welcome")
            
            logger.info(f"Processing onboarding step for user {user_id}: current_step={current_step}, message='{message}'")
            logger.info(f"User data: {user_data}")
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            # Default to demo_welcome if there's an error
            current_step = "demo_welcome"
        
        if current_step == "welcome":
            # Check if the message is a valid response to continue
            if message.lower() in ["continue", "yes", "ok", "start"]:
                # Move to GitHub credentials step
                logger.info(f"User {user_id} confirmed to continue. Moving to GitHub step.")
                update_result = self.user_manager.update_user(user_id, {"onboarding_step": "github"})
                logger.info(f"Update result: {update_result}")
                return self._get_github_prompt()
        if current_step == "demo_welcome":
            if message.lower() in ["skip", "demo", "mock"]:
                # Move to demo mode - store this in a way that won't cause DB errors
                try:
                    # First update without demo_mode in case it's not in schema
                    self.user_manager.update_user(user_id, {
                        "onboarding_step": "demo_agenda"
                    })
                    # Then try to set demo_mode separately
                    try:
                        self.user_manager.update_user(user_id, {"demo_mode": True})
                    except Exception as e:
                        logger.warning(f"Could not set demo_mode: {e}")
                except Exception as e:
                    logger.error(f"Error updating user for demo mode: {e}")
                
                # Show mock agenda
                agenda_msg = "Hi! Today on your agenda:\n\n"
                for meeting in self.mock_agenda["meetings"]:
                    agenda_msg += f"📅 {meeting['time']}: {meeting['title']}\n"
                agenda_msg += "\nTasks:\n"
                for task in self.mock_agenda["tasks"]:
                    agenda_msg += f"📋 {task}\n"
                agenda_msg += "\nLet's make a plan for today! How would you like to organize these tasks?"
                
                return agenda_msg
            else:
                # Continue with regular onboarding
                self.user_manager.update_user(user_id, {"onboarding_step": "github"})
                return self._get_github_prompt()
        
        elif current_step == "demo_agenda":
            # After user responds to agenda planning, simulate noticing an issue
            try:
                self.user_manager.update_user(user_id, {
                    "onboarding_step": "demo_issue",  # Use a specific step for the issue
                    "onboarding_completed": True
                })
            except Exception as e:
                logger.error(f"Error updating user for demo issue: {e}")
            
            # Pick a random mock issue
            import random
            issue = random.choice(self.mock_issues)
            
            return f"I notice you've been struggling with {issue}. Would you like some suggestions on how to handle this?"
            
        elif current_step == "demo_issue":
            # Final response in the demo flow
            return (
                "Great! Here are some suggestions:\n\n"
                "1. 🗓️ Block focused work time on your calendar\n"
                "2. 📋 Use the Pomodoro technique (25 min work, 5 min break)\n"
                "3. 🔔 Set up notification boundaries during deep work\n\n"
                "This concludes our demo! In the full version, I would continue to:\n"
                "• Check in with you hourly\n"
                "• Monitor your GitHub activity\n"
                "• Help decompose complex tasks\n"
                "• Provide psychological support\n\n"
                "Would you like to set up the full version now?"
            )
        
        elif current_step == "github":
            # Handle GitHub token or skip
            if message.lower() in ["skip", "later", "no"]:
                # User wants to skip GitHub setup
                logger.info(f"User {user_id} is skipping GitHub setup")
                
                # Update user data to mark GitHub setup as skipped
                try:
                    update_result = self.user_manager.update_user(user_id, {
                        "github_setup": "skipped",
                        "onboarding_step": "google"  # Move to the next step
                    })
                    logger.info(f"Update result after skipping GitHub: {update_result}")
                except Exception as e:
                    logger.error(f"Error updating user after GitHub skip: {e}")
                
                return self._get_google_prompt()
            elif self._validate_github_token(message):
                # Valid GitHub token provided
                self._save_github_credentials(user_id, message)
                
                try:
                    update_result = self.user_manager.update_user(user_id, {"onboarding_step": "google"})
                    logger.info(f"Update result after saving GitHub token: {update_result}")
                    
                    # Verify the update worked
                    updated_user = self.user_manager.get_user(user_id)
                    logger.info(f"User data after GitHub token update: {updated_user}")
                except Exception as e:
                    logger.error(f"Error updating user after GitHub token: {e}")
                
                return self._get_google_prompt()
            else:
                logger.info(f"User {user_id} provided an invalid GitHub token: '{message}'")
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
        # Note: We now handle skip separately in process_onboarding_step
        # This method now only validates actual tokens
        return len(token) == 40 and token.isalnum()
    
    def _save_github_credentials(self, user_id, token):
        """Save GitHub credentials"""
        # This method now only handles valid tokens, not skips
        # Skip handling is done directly in process_onboarding_step
        
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
