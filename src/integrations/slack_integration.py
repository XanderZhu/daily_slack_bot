import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SlackIntegration:
    """
    Handles integration with the Slack API.
    Provides methods for sending messages, getting user information, and monitoring activity.
    """
    
    def __init__(self):
        """Initialize the Slack integration with API token"""
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.bot_id = self._get_bot_id()
    
    def _get_bot_id(self):
        """Get the bot's user ID"""
        try:
            response = self.client.auth_test()
            return response["user_id"]
        except SlackApiError as e:
            logger.error(f"Error getting bot ID: {e}")
            return None
    
    def send_message(self, channel, text, blocks=None):
        """Send a message to a Slack channel or user"""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return response
        except SlackApiError as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def get_user_info(self, user_id):
        """Get information about a Slack user"""
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]
        except SlackApiError as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def get_user_presence(self, user_id):
        """Get a user's presence status (active or away)"""
        try:
            response = self.client.users_getPresence(user=user_id)
            return response["presence"]
        except SlackApiError as e:
            logger.error(f"Error getting user presence: {e}")
            return None
    
    def get_user_activity(self, user_id, days=1):
        """Get a user's activity in Slack over a period of time"""
        # This is a simplified implementation
        # In a real implementation, you would use the Slack Analytics API
        # or monitor message events over time
        
        try:
            # Get channels the user is in
            response = self.client.users_conversations(
                user=user_id,
                types="public_channel,private_channel"
            )
            channels = response["channels"]
            
            activity = {
                "message_count": 0,
                "channels_active": 0,
                "last_active": None
            }
            
            # For each channel, check for recent messages from the user
            for channel in channels:
                try:
                    # Get recent messages in the channel
                    history = self.client.conversations_history(
                        channel=channel["id"],
                        limit=100  # Adjust as needed
                    )
                    
                    # Count messages from the user
                    user_messages = [
                        msg for msg in history["messages"]
                        if msg.get("user") == user_id
                    ]
                    
                    if user_messages:
                        activity["message_count"] += len(user_messages)
                        activity["channels_active"] += 1
                        
                        # Update last active time if newer
                        latest_ts = max(float(msg["ts"]) for msg in user_messages)
                        if not activity["last_active"] or latest_ts > activity["last_active"]:
                            activity["last_active"] = latest_ts
                
                except SlackApiError as e:
                    logger.warning(f"Error getting channel history for {channel['id']}: {e}")
                    continue
            
            return activity
            
        except SlackApiError as e:
            logger.error(f"Error getting user activity: {e}")
            return None
    
    def get_all_users(self):
        """Get a list of all users in the workspace"""
        try:
            response = self.client.users_list()
            return response["members"]
        except SlackApiError as e:
            logger.error(f"Error getting users list: {e}")
            return []
    
    def get_active_users(self):
        """Get a list of active users (not bots, not deleted)"""
        try:
            all_users = self.get_all_users()
            
            active_users = [
                user for user in all_users
                if not user.get("is_bot", False)
                and not user.get("deleted", False)
                and not user.get("is_restricted", False)
                and not user.get("is_ultra_restricted", False)
            ]
            
            return active_users
        except Exception as e:
            logger.error(f"Error filtering active users: {e}")
            return []
    
    def create_welcome_blocks(self, meetings, tasks):
        """Create formatted message blocks for the welcome message"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Good morning! Here's your daily summary:",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add meetings section
        meeting_text = "*Today's Meetings:*\n"
        if meetings:
            for meeting in meetings:
                meeting_text += f"• {meeting['time']}: {meeting['title']}\n"
        else:
            meeting_text += "No meetings scheduled for today.\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": meeting_text
            }
        })
        
        # Add tasks section
        task_text = "*Pending Tasks:*\n"
        if tasks:
            for task in tasks:
                task_text += f"• {task['title']}\n"
        else:
            task_text += "No pending tasks found.\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": task_text
            }
        })
        
        # Add planning prompt
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Let's plan what you'll do today! What are your top priorities?"
            }
        })
        
        # Add actions
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Plan My Day",
                        "emoji": True
                    },
                    "value": "plan_day",
                    "action_id": "plan_day"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Show All Tasks",
                        "emoji": True
                    },
                    "value": "show_tasks",
                    "action_id": "show_tasks"
                }
            ]
        })
        
        return blocks
