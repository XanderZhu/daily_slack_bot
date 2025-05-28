#!/usr/bin/env python3
import os
import logging
import time
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from src.agents.daily_slack_team import create_daily_slack_team
from src.utils.scheduler import setup_scheduler
from src.utils.initializer import Initializer
from src.utils.onboarding import OnboardingManager
from src.utils.user_manager import UserManager
from src.utils.activity_monitor import ActivityMonitor

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"slack_bot_{time.strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize components
initializer = Initializer()
components = initializer.initialize_all()

# Initialize Slack app
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize agent team
agent_team = create_daily_slack_team()

# Make components available to the agent team
agent_team.set_components(components)

# User manager for tracking user data
user_manager = components['user_manager']

# Activity monitor for tracking user activity
activity_monitor = components['activity_monitor']

# Onboarding manager for new users
onboarding_manager = OnboardingManager(user_manager)


async def ensure_user_exists(user_id):
    """Ensure a user exists in the database, creating them if they don't"""
    if not user_manager:
        return None
        
    # Get user data
    user_data = user_manager.get_user(user_id)
    
    # If user doesn't exist in the database, create them
    if not user_data:
        try:
            # Get user info from Slack
            user_info = await app.client.users_info(user=user_id)
            slack_user = user_info["user"]
            
            # Create basic user profile
            new_user_data = {
                "slack_id": user_id,
                "name": slack_user.get("real_name", ""),
                "email": slack_user.get("profile", {}).get("email", ""),
                "created_at": datetime.now().isoformat(),
                "onboarding_started": False,
                "onboarding_completed": False
            }
            
            # Create user in the database
            user_data = user_manager.update_user(user_id, new_user_data)
            logger.info(f"Created new user in SQLite database: {user_id}")
        except Exception as e:
            logger.error(f"Error creating user in database: {e}")
            return None
    
    return user_data

@app.event("app_mention")
async def handle_app_mention(event, say):
    """Handle when the bot is mentioned in a channel"""
    user_id = event["user"]
    text = event["text"]
    channel_id = event["channel"]
    
    logger.info(f"App mention from user {user_id} in channel {channel_id}: {text}")
    
    # Ensure user exists in the database
    user_data = await ensure_user_exists(user_id)
    
    # Log the interaction
    if user_manager:
        user_manager.log_interaction(user_id, "app_mention", {"text": text, "channel": channel_id})
    
    # Check if user needs onboarding
    if not onboarding_manager.check_onboarding_status(user_id):
        # Start onboarding in a direct message
        welcome_message = onboarding_manager.start_onboarding(user_id)
        await app.client.chat_postMessage(
            channel=user_id,
            text="I need to set up your account. I've sent you a direct message to get started."
        )
        await app.client.chat_postMessage(
            channel=user_id,
            text=welcome_message
        )
        return
    
    # Process the mention through the agent team
    response = await agent_team.invoke(user_id, text, request_type="mention")
    await say(response)

@app.event("message")
async def handle_direct_message(event, say):
    """Handle direct messages to the bot"""
    if event.get("channel_type") == "im":
        # Safely get user ID with a default value
        user_id = event.get("user")
        if not user_id:
            logger.error(f"No user ID found in event: {event}")
            await say("I'm sorry, but I couldn't process your message. Please try again.")
            return
            
        text = event.get("text", "")
        channel_id = event.get("channel")
        
        # Ignore messages from bots
        if event.get("bot_id"):
            return
        
        logger.info(f"Direct message from user {user_id}: {text}")
        
        # Ensure user exists in the database
        user_data = await ensure_user_exists(user_id)
        
        # Log the interaction
        if user_manager:
            user_manager.log_interaction(user_id, "direct_message", {"text": text})
        
        # Check if user is in onboarding process
        logger.info(f"Checking onboarding status for user {user_id}: {user_data}")
        
        # Always get fresh user data directly from SQLite to avoid cache issues
        if user_manager.db:
            fresh_user_data = user_manager.db.get_user(user_id)
            logger.info(f"Fresh user data from SQLite: {fresh_user_data}")
            if fresh_user_data:
                user_data = fresh_user_data
                # Update cache
                user_manager.user_cache[user_id] = fresh_user_data
        
        if user_data and user_data.get("onboarding_started", False) and not user_data.get("onboarding_completed", False):
            logger.info(f"User {user_id} is in onboarding process. Processing step with message: '{text}'")
            # Process onboarding step
            response = onboarding_manager.process_onboarding_step(user_id, text)
            logger.info(f"Onboarding response: {response}")
            await say(response)
            return
        
        # Check if this is a first-time user
        if not user_data or not user_data.get("onboarding_started", False):
            logger.info(f"Starting onboarding for new user {user_id}")
            # Start onboarding
            welcome_message = onboarding_manager.start_onboarding(user_id)
            await say(welcome_message)
            return
        
        # Process the direct message through the agent team
        response = await agent_team.invoke(user_id, text, request_type="direct_message")
        await say(response)

@app.action("plan_day")
async def handle_plan_day(ack, body, say):
    """Handle the Plan My Day button click"""
    await ack()
    user_id = body["user"]["id"]
    
    logger.info(f"Plan day action from user {user_id}")
    
    # Ensure user exists in the database
    user_data = await ensure_user_exists(user_id)
    
    # Log the interaction
    if user_manager:
        user_manager.log_interaction(user_id, "plan_day_button")
    
    # Use the agent team to create a plan
    response = await agent_team.invoke(user_id, "Help me plan my day", request_type="direct_message")
    await say(response)

@app.action("show_tasks")
async def handle_show_tasks(ack, body, say):
    """Handle the Show All Tasks button click"""
    await ack()
    user_id = body["user"]["id"]
    
    logger.info(f"Show tasks action from user {user_id}")
    
    # Ensure user exists in the database
    user_data = await ensure_user_exists(user_id)
    
    # Log the interaction
    if user_manager:
        user_manager.log_interaction(user_id, "show_tasks_button")
    
    # Use the agent team to get tasks
    tasks = agent_team.get_pending_tasks(user_id)
    
    if tasks:
        response = "Here are all your pending tasks:\n\n"
        for task in tasks:
            response += f"• *{task.title}*\n"
            if task.priority:
                response += f"  Priority: {task.priority}\n"
            if task.description:
                response += f"  Description: {task.description}\n"
            response += "\n"
    else:
        response = "You don't have any pending tasks at the moment."
    
    await say(response)

async def main():
    """Main function to start the bot"""
    logger.info("Starting Daily Slack Bot with Socket Mode...")
    
    # Check for required environment variables
    slack_app_token = os.environ.get("SLACK_APP_TOKEN")
    if not slack_app_token:
        logger.error("SLACK_APP_TOKEN is not set in environment variables")
        return
    
    # Check for LiteLLM API key
    litellm_api_key = os.environ.get("LITELLM_API_KEY")
    if not litellm_api_key:
        logger.warning("LITELLM_API_KEY is not set in environment variables")
    
    # Check component status
    status = initializer.check_status()
    logger.info(f"Component status: {status}")
    
    # Set up scheduled tasks
    setup_scheduler(app, agent_team)
    
    # Start the Socket Mode handler
    try:
        logger.info("Starting the Slack bot with Socket Mode")
        
        # Patch the WebSocket ping method to handle string encoding
        # This is needed because of an issue in aiohttp WebSocket implementation
        import aiohttp
        from functools import wraps
        
        # Store the original ping method
        original_ping = aiohttp.ClientWebSocketResponse.ping
        
        # Create a patched ping method that handles encoding
        @wraps(original_ping)
        async def patched_ping(self, message=b''):
            if isinstance(message, str):
                message = message.encode('utf-8')
            return await original_ping(self, message)
        
        # Apply the monkey patch
        aiohttp.ClientWebSocketResponse.ping = patched_ping
        
        # Create the handler
        handler = AsyncSocketModeHandler(app, slack_app_token)
        
        # Start the handler
        await handler.start_async()
    except KeyboardInterrupt:
        logger.info("Shutting down the Slack bot")
    except Exception as e:
        logger.error(f"Error running the Slack bot: {e}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    asyncio.run(main())