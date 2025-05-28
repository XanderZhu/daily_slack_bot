#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.agents.agent_network import create_agent_network
from src.utils.scheduler import setup_scheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize agent network
agent_network = create_agent_network()

@app.event("app_mention")
def handle_app_mention(event, say):
    """Handle when the bot is mentioned in a channel"""
    user_id = event["user"]
    text = event["text"]
    
    # Process the mention through the agent network
    response = agent_network.process_mention(user_id, text)
    say(response)

@app.event("message")
def handle_direct_message(event, say):
    """Handle direct messages to the bot"""
    if event.get("channel_type") == "im":
        user_id = event["user"]
        text = event["text"]
        
        # Process the direct message through the agent network
        response = agent_network.process_direct_message(user_id, text)
        say(response)

def main():
    """Main function to start the bot"""
    logger.info("Starting Daily Slack Bot...")
    
    # Set up scheduled tasks
    setup_scheduler(app, agent_network)
    
    # Start the Socket Mode handler
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == "__main__":
    main()
