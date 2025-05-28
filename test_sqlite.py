#!/usr/bin/env python3
import logging
from src.integrations.sqlite_integration import SQLiteIntegration
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sqlite_operations():
    # Initialize SQLite integration
    db = SQLiteIntegration()
    
    # Test creating a user
    logger.info("Testing create_user...")
    test_user = {
        'slack_id': 'test_user_123',
        'name': 'Test User',
        'email': 'test@example.com',
        'preferences': {
            'notifications': True,
            'daily_summary': True
        }
    }
    
    user_result = db.create_user(test_user)
    if user_result:
        logger.info(f"Successfully created user: {user_result}")
    else:
        logger.error("Failed to create user")
    
    # Test getting a user
    logger.info("Testing get_user...")
    user = db.get_user('test_user_123')
    if user:
        logger.info(f"Retrieved user: {user}")
    else:
        logger.error("Failed to retrieve user")
    
    # Test updating a user
    logger.info("Testing update_user...")
    update_data = {
        'name': 'Updated Test User',
        'preferences': {
            'notifications': False,
            'daily_summary': True,
            'weekly_report': True
        }
    }
    
    updated_user = db.update_user('test_user_123', update_data)
    if updated_user:
        logger.info(f"Successfully updated user: {updated_user}")
    else:
        logger.error("Failed to update user")
    
    # Test storing credentials
    logger.info("Testing store_credentials...")
    test_creds = {
        'api_key': 'test_key_123',
        'refresh_token': 'test_refresh_token',
        'expires_at': (datetime.now().timestamp() + 3600)
    }
    
    cred_result = db.store_credentials('test_user_123', 'github', test_creds)
    if cred_result:
        logger.info(f"Successfully stored credentials: {cred_result}")
    else:
        logger.error("Failed to store credentials")
    
    # Test getting credentials
    logger.info("Testing get_credentials...")
    creds = db.get_credentials('test_user_123', 'github')
    if creds:
        logger.info(f"Retrieved credentials: {creds}")
    else:
        logger.error("Failed to retrieve credentials")
    
    # Test logging an interaction
    logger.info("Testing log_interaction...")
    interaction_details = {
        'message': 'Hello, how can I help you today?',
        'channel': 'direct_message',
        'timestamp': datetime.now().isoformat()
    }
    
    interaction_result = db.log_interaction('test_user_123', 'greeting', interaction_details)
    if interaction_result:
        logger.info(f"Successfully logged interaction: {interaction_result}")
    else:
        logger.error("Failed to log interaction")
    
    # Test getting recent interactions
    logger.info("Testing get_recent_interactions...")
    interactions = db.get_recent_interactions('test_user_123')
    logger.info(f"Retrieved {len(interactions)} interactions")
    for interaction in interactions:
        logger.info(f"Interaction: {interaction}")
    
    # Test getting all users
    logger.info("Testing get_all_users...")
    all_users = db.get_all_users()
    logger.info(f"Retrieved {len(all_users)} users")
    for user in all_users:
        logger.info(f"User: {user}")
    
    # Close the database connection
    db.close()
    logger.info("SQLite operations test completed")

if __name__ == "__main__":
    test_sqlite_operations()
