#!/usr/bin/env python3
"""
Simple test script to send a single request to the Daily Slack Bot
"""

import os
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
    """Main function to test the bot with a direct request"""
    logger.info("Starting simple test script...")
    
    # Initialize components
    initializer = Initializer()
    components = initializer.initialize_all()
    
    # Initialize agent team
    agent_team = create_daily_slack_team()
    
    # Make components available to the agent team
    agent_team.set_components(components)
    
    # Test user ID
    user_id = "test_user"
    
    # Test message - change this to test different requests
    test_message = "Can you help me plan my day?"
    request_type = "direct_message"  # Options: "welcome", "checkin", "activity_check", "direct_message", "mention"
    
    print(f"\n=== PROCESSING REQUEST: '{test_message}' (Type: {request_type}) ===")
    response = await agent_team.invoke(user_id, test_message, request_type=request_type)
    print("\nRESPONSE:")
    print(response)
    print("\n===============================")
    
    logger.info("Test completed")

if __name__ == "__main__":
    asyncio.run(main())
