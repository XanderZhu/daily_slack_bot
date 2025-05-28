#!/usr/bin/env python3
import os
import logging
from datetime import datetime
import httpx
from postgrest._sync.client import SyncPostgrestClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_create_user_with_service_role():
    # Check for service role key in environment
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        logger.error("Supabase URL or key not set in environment variables")
        return
    
    logger.info(f"Using Supabase URL: {url}")
    logger.info(f"Using key: {key[:5]}...{key[-5:] if len(key) > 10 else ''}")
    
    # Create test user data
    test_data = {
        'slack_id': f'test_user_{datetime.now().timestamp()}',  # Use timestamp to ensure uniqueness
        'name': 'Test User',
        'created_at': datetime.now().isoformat()
    }
    
    try:
        # Set up headers with service role key
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"  # This tells Supabase to return the created record
        }
        
        # Create a direct connection to Supabase
        rest_url = f"{url}/rest/v1"
        
        # Initialize the PostgrestClient with service role key
        client = SyncPostgrestClient(
            base_url=rest_url,
            schema="public",
            headers=headers
        )
        
        # Try to create user directly
        logger.info(f"Attempting to create user with data: {test_data}")
        response = client.from_("users").insert(test_data).execute()
        
        logger.info(f"Response: {response}")
        
        if response.data and len(response.data) > 0:
            logger.info(f"Successfully created user: {response.data[0]}")
            return response.data[0]
        else:
            logger.error(f"Failed to create user. Response: {response}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None

if __name__ == "__main__":
    test_create_user_with_service_role()
