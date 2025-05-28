#!/usr/bin/env python3
"""
Test script to send requests to the Daily Slack Bot
This script allows you to test the bot's functionality by simulating Slack events
"""

import os
import json
import asyncio
import logging
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
    """Main function to test the bot with direct requests"""
    logger.info("Starting test requests script...")
    
    # Initialize components
    initializer = Initializer()
    components = initializer.initialize_all()
    
    # Initialize agent team
    agent_team = create_daily_slack_team()
    
    # Make components available to the agent team
    agent_team.set_components(components)
    
    # Test user ID
    user_id = "test_user"
    
    # Menu for test options
    while True:
        print("\n=== Daily Slack Bot Test Menu ===")
        print("1. Send welcome message")
        print("2. Send hourly check-in")
        print("3. Check user activity")
        print("4. Send custom message")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            # Test welcome message
            print("\n=== WELCOME MESSAGE ===")
            welcome_message = await agent_team.invoke(user_id, "", request_type="welcome")
            print(welcome_message)
            print("=======================\n")
            
        elif choice == "2":
            # Test hourly check-in
            print("\n=== HOURLY CHECK-IN ===")
            checkin_message = await agent_team.invoke(user_id, "", request_type="checkin")
            print(checkin_message)
            print("=======================\n")
            
        elif choice == "3":
            # Test activity check
            print("\n=== ACTIVITY CHECK ===")
            activity_message = await agent_team.invoke(user_id, "", request_type="activity_check")
            print(activity_message if activity_message else "No activity issues detected.")
            print("=======================\n")
            
        elif choice == "4":
            # Test custom message
            message = input("\nEnter your message to the bot: ")
            print(f"\n=== PROCESSING MESSAGE: '{message}' ===")
            response = await agent_team.invoke(user_id, message, request_type="direct_message")
            print(response)
            print("===============================\n")
            
        elif choice == "5":
            # Exit
            print("Exiting test script...")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
    
    logger.info("Test requests script completed")

if __name__ == "__main__":
    asyncio.run(main())
