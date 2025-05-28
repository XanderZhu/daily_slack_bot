#!/usr/bin/env python3
import os
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from src.agents.agent_network import create_agent_network
from src.utils.scheduler import setup_scheduler
from src.utils.initializer import Initializer
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
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize agent network
agent_network = create_agent_network()

# Make components available to the agent network
agent_network.set_components(components)

# User manager for tracking user data
user_manager = components['user_manager']

# Activity monitor for tracking user activity
activity_monitor = components['activity_monitor']

@app.event("app_mention")
def handle_app_mention(event, say):
    """Handle when the bot is mentioned in a channel"""
    user_id = event["user"]
    text = event["text"]
    channel_id = event["channel"]
    
    logger.info(f"App mention from user {user_id} in channel {channel_id}: {text}")
    
    # Log the interaction
    if user_manager:
        user_manager.log_interaction(user_id, "app_mention", {"text": text, "channel": channel_id})
    
    # Process the mention through the agent network
    response = agent_network.process_mention(user_id, text)
    say(response)

@app.event("message")
def handle_direct_message(event, say):
    """Handle direct messages to the bot"""
    if event.get("channel_type") == "im":
        user_id = event["user"]
        text = event["text"]
        channel_id = event["channel"]
        
        logger.info(f"Direct message from user {user_id}: {text}")
        
        # Log the interaction
        if user_manager:
            user_manager.log_interaction(user_id, "direct_message", {"text": text})
        
        # Process the direct message through the agent network
        response = agent_network.process_direct_message(user_id, text)
        say(response)

@app.action("plan_day")
def handle_plan_day(ack, body, say):
    """Handle the Plan My Day button click"""
    ack()
    user_id = body["user"]["id"]
    
    logger.info(f"Plan day action from user {user_id}")
    
    # Log the interaction
    if user_manager:
        user_manager.log_interaction(user_id, "plan_day_button")
    
    # Get the daily planner agent to create a plan
    response = agent_network.daily_planner.process_request(user_id, "Help me plan my day")
    say(response)

@app.action("show_tasks")
def handle_show_tasks(ack, body, say):
    """Handle the Show All Tasks button click"""
    ack()
    user_id = body["user"]["id"]
    
    logger.info(f"Show tasks action from user {user_id}")
    
    # Log the interaction
    if user_manager:
        user_manager.log_interaction(user_id, "show_tasks_button")
    
    # Get the project analyst agent to show tasks
    tasks = agent_network.project_analyst.get_pending_tasks(user_id)
    
    if tasks:
        response = "Here are all your pending tasks:\n\n"
        for task in tasks:
            response += f"• *{task['title']}*\n"
            if 'priority' in task:
                response += f"  Priority: {task['priority']}\n"
            if 'source' in task:
                response += f"  Source: {task['source']}\n"
            response += "\n"
    else:
        response = "You don't have any pending tasks at the moment."
    
    say(response)

def main():
    """Main function to start the bot"""
    logger.info("Starting Daily Slack Bot...")
    
    # Check component status
    status = initializer.check_status()
    logger.info(f"Component status: {status}")
    
    # Set up scheduled tasks
    setup_scheduler(app, agent_network)
    
    # Start the Socket Mode handler
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    
    try:
        logger.info("Starting the Slack bot")
        handler.start()
    except KeyboardInterrupt:
        logger.info("Shutting down the Slack bot")
    except Exception as e:
        logger.error(f"Error running the Slack bot: {e}")

if __name__ == "__main__":
    main()