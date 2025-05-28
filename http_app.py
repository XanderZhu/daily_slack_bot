#!/usr/bin/env python3
import os
import logging
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi import AsyncSlackRequestHandler

from src.agents.daily_slack_team import create_daily_slack_team
from src.utils.scheduler import setup_scheduler
from src.utils.initializer import Initializer
from src.utils.onboarding import OnboardingManager

from fastapi import FastAPI, Request
import uvicorn

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

@app.event("app_mention")
async def handle_app_mention(event, say):
    """Handle when the bot is mentioned in a channel"""
    user_id = event["user"]
    text = event["text"]
    channel_id = event["channel"]
    
    logger.info(f"App mention from user {user_id} in channel {channel_id}: {text}")
    
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
        user_id = event["user"]
        text = event["text"]
        channel_id = event["channel"]
        
        # Ignore messages from bots
        if event.get("bot_id"):
            return
        
        logger.info(f"Direct message from user {user_id}: {text}")
        
        # Log the interaction
        if user_manager:
            user_manager.log_interaction(user_id, "direct_message", {"text": text})
        
        # Check if user is in onboarding process
        user_data = user_manager.get_user(user_id)
        if user_data and user_data.get("onboarding_started", False) and not user_data.get("onboarding_completed", False):
            # Process onboarding step
            response = onboarding_manager.process_onboarding_step(user_id, text)
            await say(response)
            return
        
        # Check if this is a first-time user
        if not user_data or not user_data.get("onboarding_started", False):
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

# Set up FastAPI
api = FastAPI()
handler = AsyncSlackRequestHandler(app)

@api.post("/slack/events")
async def endpoint(req: Request):
    return await handler.handle(req)

@api.get("/")
async def health_check():
    return {"status": "ok"}

# Set up scheduled tasks
setup_scheduler(app, agent_team)

if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(api, host="0.0.0.0", port=port)
