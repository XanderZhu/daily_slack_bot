#!/usr/bin/env python3
import logging
from src.integrations.supabase_integration import SupabaseIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_create_user():
    # Initialize Supabase client
    client = SupabaseIntegration()
    
    if not client.client:
        logger.error("Failed to initialize Supabase client")
        return
    
    # Create test user data
    test_data = {
        'name': 'Test User',
        'slack_id': 'test_user_123',
        'email': 'test@example.com',
        'created_at': '2025-05-28T20:34:44+07:00',
        'updated_at': '2025-05-28T20:34:44+07:00',
        'status': 'active'
    }
    
    # Try to create user
    logger.info(f"Attempting to create user with data: {test_data}")
    result = client.create_user(test_data)
    
    if result:
        logger.info(f"Successfully created user: {result}")
    else:
        logger.error("Failed to create user")
    
    # Try to get all users
    users = client.get_all_users()
    logger.info(f"Retrieved {len(users)} users")
    for user in users:
        logger.info(f"User: {user}")

if __name__ == "__main__":
    test_create_user()
