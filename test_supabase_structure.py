#!/usr/bin/env python3
import logging
import json
from src.integrations.supabase_integration import SupabaseIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_table_structure():
    # Initialize Supabase client
    client = SupabaseIntegration()
    
    if not client.client:
        logger.error("Failed to initialize Supabase client")
        return
    
    try:
        # Try to get the structure by examining the response
        response = client.client.table('users').select('*').limit(0).execute()
        logger.info(f"Response object: {response}")
        logger.info(f"Response type: {type(response)}")
        
        # Try to access response attributes to understand structure
        if hasattr(response, 'data'):
            logger.info(f"Response data: {response.data}")
        
        if hasattr(response, 'count'):
            logger.info(f"Response count: {response.count}")
        
        if hasattr(response, 'error'):
            logger.info(f"Response error: {response.error}")
            
        # Try to get table structure from a different approach
        # This might give us column information
        try:
            # Try to get column info from a system table if accessible
            info_query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND table_schema = 'public'
            """
            schema_info = client.client.table('users').select('*').execute()
            logger.info(f"Schema info: {schema_info}")
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
        
        # Try to create a minimal user with just slack_id
        minimal_user = {
            'slack_id': 'test_minimal_123'
        }
        
        logger.info(f"Attempting to create minimal user with data: {minimal_user}")
        result = client.create_user(minimal_user)
        
        if result:
            logger.info(f"Successfully created minimal user: {result}")
            # Now we can see what fields are in the response
            logger.info(f"Fields in user record: {list(result.keys())}")
        else:
            logger.error("Failed to create minimal user")
            
    except Exception as e:
        logger.error(f"Error inspecting table structure: {e}")

if __name__ == "__main__":
    inspect_table_structure()
