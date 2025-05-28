#!/usr/bin/env python3
import logging
from src.integrations.supabase_integration import SupabaseIntegration
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_supabase_operations():
    # Initialize Supabase client
    client = SupabaseIntegration()
    
    if not client.client:
        logger.error("Failed to initialize Supabase client")
        return
    
    # Test getting all users (this worked before)
    logger.info("Testing get_all_users...")
    users = client.get_all_users()
    logger.info(f"Retrieved {len(users)} users")
    
    # Test logging an interaction (might have different security policies)
    logger.info("Testing log_interaction...")
    interaction_result = client.log_interaction(
        slack_id="test_user_123",
        interaction_type="test",
        details={"message": "Testing Supabase integration"}
    )
    
    if interaction_result:
        logger.info(f"Successfully logged interaction: {interaction_result}")
    else:
        logger.error("Failed to log interaction")
    
    # Test getting recent interactions
    logger.info("Testing get_recent_interactions...")
    interactions = client.get_recent_interactions(slack_id="test_user_123")
    logger.info(f"Retrieved {len(interactions)} interactions")
    for interaction in interactions:
        logger.info(f"Interaction: {interaction}")
    
    # Test storing credentials (might have different security policies)
    logger.info("Testing store_credentials...")
    cred_result = client.store_credentials(
        slack_id="test_user_123",
        credential_type="test",
        credentials={"api_key": "test_key_123"}
    )
    
    if cred_result:
        logger.info(f"Successfully stored credentials: {cred_result}")
    else:
        logger.error("Failed to store credentials")
    
    # Test getting credentials
    logger.info("Testing get_credentials...")
    creds = client.get_credentials(slack_id="test_user_123", credential_type="test")
    if creds:
        logger.info(f"Retrieved credentials: {creds}")
    else:
        logger.info("No credentials found")

if __name__ == "__main__":
    test_supabase_operations()
