#!/usr/bin/env python3
import logging
from src.utils.user_manager import UserManager
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_manager():
    # Initialize UserManager with SQLite integration
    user_manager = UserManager()
    
    # Test creating a user
    logger.info("Testing user creation...")
    test_user = {
        'slack_id': 'test_manager_123',
        'name': 'Test Manager User',
        'email': 'test_manager@example.com',
        'preferences': {
            'notifications': True,
            'daily_summary': True
        }
    }
    
    result = user_manager.update_user('test_manager_123', test_user)
    if result:
        logger.info(f"Successfully created user: {result}")
    else:
        logger.error("Failed to create user")
    
    # Test getting a user
    logger.info("Testing get_user...")
    user = user_manager.get_user('test_manager_123')
    if user:
        logger.info(f"Retrieved user: {user}")
    else:
        logger.error("Failed to retrieve user")
    
    # Test updating preferences
    logger.info("Testing update_preferences...")
    prefs = {
        'notifications': False,
        'weekly_report': True
    }
    
    updated_user = user_manager.update_preferences('test_manager_123', prefs)
    if updated_user:
        logger.info(f"Updated preferences: {updated_user.get('preferences', {})}")
    else:
        logger.error("Failed to update preferences")
    
    # Test storing credentials
    logger.info("Testing store_credentials...")
    test_creds = {
        'api_key': 'test_manager_key_123',
        'refresh_token': 'test_manager_refresh_token',
        'expires_at': (datetime.now().timestamp() + 3600)
    }
    
    cred_result = user_manager.store_credentials('test_manager_123', 'github', test_creds)
    if cred_result:
        logger.info(f"Successfully stored credentials: {cred_result}")
    else:
        logger.error("Failed to store credentials")
    
    # Test getting credentials
    logger.info("Testing get_credentials...")
    creds = user_manager.get_credentials('test_manager_123', 'github')
    if creds:
        logger.info(f"Retrieved credentials: {creds}")
    else:
        logger.error("Failed to retrieve credentials")
    
    # Test logging an interaction
    logger.info("Testing log_interaction...")
    interaction_details = {
        'message': 'Hello from user manager test',
        'channel': 'direct_message',
        'timestamp': datetime.now().isoformat()
    }
    
    interaction_result = user_manager.log_interaction('test_manager_123', 'greeting', interaction_details)
    if interaction_result:
        logger.info(f"Successfully logged interaction: {interaction_result}")
    else:
        logger.error("Failed to log interaction")
    
    # Test getting recent interactions
    logger.info("Testing get_recent_interactions...")
    interactions = user_manager.get_recent_interactions('test_manager_123')
    logger.info(f"Retrieved {len(interactions)} interactions")
    for interaction in interactions:
        logger.info(f"Interaction: {interaction}")
    
    # Test getting all users
    logger.info("Testing get_all_users...")
    all_users = user_manager.get_all_users()
    logger.info(f"Retrieved {len(all_users)} users")
    for user in all_users:
        logger.info(f"User: {user}")
    
    logger.info("UserManager test completed")

if __name__ == "__main__":
    test_user_manager()
