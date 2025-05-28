#!/usr/bin/env python3
"""
Test script for the Daily Slack Bot
This script allows you to test the bot's functionality locally without connecting to Slack.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from src.agents.daily_slack_team import create_daily_slack_team
from src.utils.initializer import Initializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def main():
    """Main function to test the bot"""
    logger.info("Starting Daily Slack Bot test...")
    
    # Initialize components
    initializer = Initializer()
    components = initializer.initialize_all()
    
    # Initialize agent team
    agent_team = create_daily_slack_team()
    
    # Make components available to the agent team
    agent_team.set_components(components)
    
    # Test welcome message
    user_id = "test_user"
    welcome_message = await agent_team.invoke(user_id, "", request_type="welcome")
    print("\n=== WELCOME MESSAGE ===")
    print(welcome_message)
    print("=======================\n")
    
    # Test hourly check-in
    checkin_message = await agent_team.invoke(user_id, "", request_type="checkin")
    print("\n=== HOURLY CHECK-IN ===")
    print(checkin_message)
    print("=======================\n")
    
    # Test direct message processing
    test_messages = [
        "Can you help me plan my day?",
        "I need to break down a complex task",
        "I'm feeling stuck with my current project",
        "Can you help me with some code?"
    ]
    
    for message in test_messages:
        print(f"\n=== PROCESSING MESSAGE: '{message}' ===")
        response = await agent_team.invoke(user_id, message, request_type="direct_message")
        print(response)
        print("===============================\n")
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    asyncio.run(main())
