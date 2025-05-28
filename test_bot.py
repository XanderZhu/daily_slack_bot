#!/usr/bin/env python3
"""
Test script for the Daily Slack Bot
This script allows you to test the bot's functionality locally without connecting to Slack.
"""

import os
import logging
from dotenv import load_dotenv
from src.agents.agent_network import create_agent_network
from src.utils.initializer import Initializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """Main function to test the bot"""
    logger.info("Starting Daily Slack Bot test...")
    
    # Initialize components
    initializer = Initializer()
    components = initializer.initialize_all()
    
    # Initialize agent network
    agent_network = create_agent_network()
    
    # Make components available to the agent network
    agent_network.set_components(components)
    
    # Test welcome message
    user_id = "test_user"
    welcome_message = agent_network.send_welcome_message(user_id)
    print("\n=== WELCOME MESSAGE ===")
    print(welcome_message)
    print("=======================\n")
    
    # Test hourly check-in
    checkin_message = agent_network.send_hourly_checkin(user_id)
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
        response = agent_network.process_direct_message(user_id, message)
        print(response)
        print("===============================\n")
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    main()
