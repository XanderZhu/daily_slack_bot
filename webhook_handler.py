#!/usr/bin/env python3
import os
import logging
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.flask import SlackRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Slack app
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Handle Slack events, including URL verification
    """
    # Get the request data
    data = request.get_json()
    logger.info(f"Received Slack event: {data.get('type', 'unknown')}")
    
    # Handle URL verification challenge
    if data and data.get("type") == "url_verification":
        logger.info("Handling URL verification challenge")
        return jsonify({
            "challenge": data.get("challenge")
        })
    
    # Pass all other events to the Slack app
    return handler.handle(request)

@app.event("app_mention")
async def handle_app_mention(event, say):
    """Handle when the bot is mentioned in a channel"""
    user_id = event["user"]
    text = event["text"]
    channel_id = event["channel"]
    
    logger.info(f"App mention from user {user_id} in channel {channel_id}: {text}")
    
    # Simple response for testing
    await say(f"Hello <@{user_id}>! I received your message: {text}")

@app.event("message")
async def handle_direct_message(event, say):
    """Handle direct messages to the bot"""
    if event.get("channel_type") == "im":
        user_id = event["user"]
        text = event["text"]
        
        # Ignore messages from bots
        if event.get("bot_id"):
            return
        
        logger.info(f"Direct message from user {user_id}: {text}")
        
        # Simple response for testing
        await say(f"Hello <@{user_id}>! I received your direct message: {text}")

if __name__ == "__main__":
    # Run the Flask app
    flask_app.run(host="0.0.0.0", port=8080, debug=True)
