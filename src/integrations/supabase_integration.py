import os
import logging
from datetime import datetime
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from postgrest import PostgrestClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseIntegration:
    """Integration with Supabase for data storage"""
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            
            if not url or not key:
                logger.error("Supabase URL or key not set in environment variables")
                self.client = None
                return
            
            # Create a custom client implementation
            try:
                # Create a custom client class that mimics the Supabase client
                class CustomSupabaseClient:
                    def __init__(self, url, key):
                        self.url = url
                        self.key = key
                        self.rest_url = f"{url}/rest/v1"
                        self.auth_url = f"{url}/auth/v1"
                        self.storage_url = f"{url}/storage/v1"
                        self.headers = {
                            "apikey": key,
                            "Authorization": f"Bearer {key}",
                            "Content-Type": "application/json"
                        }
                    
                    def table(self, table_name):
                        # Create a PostgrestClient for the table using the correct parameters
                        from postgrest._sync.client import SyncPostgrestClient
                        
                        # Initialize the client with the correct parameters
                        client = SyncPostgrestClient(
                            base_url=self.rest_url,
                            schema="public",
                            headers=self.headers
                        )
                        
                        # Return the table query builder
                        return client.from_(table_name)
                
                # Initialize the custom client
                self.client = CustomSupabaseClient(url, key)
                logger.info("Custom Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing custom Supabase client: {e}")
                self.client = None
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {e}")
            self.client = None
    
    def get_user(self, slack_id):
        """Get user data from Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            response = self.client.table("users").select("*").eq("slack_id", slack_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting user from Supabase: {e}")
            return None
    
    def create_user(self, user_data):
        """Create a new user in Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            response = self.client.table("users").insert(user_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                return None
        except Exception as e:
            logger.error(f"Error creating user in Supabase: {e}")
            return None
    
    def update_user(self, slack_id, user_data):
        """Update user data in Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            user_data["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"Updating user {slack_id} in Supabase with data: {user_data}")
            
            # Update user data
            response = self.client.table("users").update(user_data).eq("slack_id", slack_id).execute()
            
            if response.data:
                logger.info(f"Successfully updated user in Supabase: {slack_id}")
                logger.info(f"Updated user data: {response.data[0]}")
                return response.data[0]
            else:
                logger.error(f"No data returned from Supabase user update for {slack_id}")
                # Check if user exists
                check = self.client.table("users").select("*").eq("slack_id", slack_id).execute()
                logger.error(f"User check result: {check.data}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating user in Supabase: {e}")
            logger.exception("Detailed error information:")
            return None
    
    def store_credentials(self, slack_id, credential_type, credentials):
        """Store user credentials in Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        
        try:
            # Prepare credential data
            cred_data = {
                "slack_id": slack_id,
                "credential_type": credential_type,
                "data": credentials,
                "created_at": datetime.now().isoformat()
            }
            
            # Check if credentials already exist
            existing = self.client.table("credentials").select("*").eq("slack_id", slack_id).eq("credential_type", credential_type).execute()
            
            if existing.data:
                # Update existing credentials
                response = self.client.table("credentials").update({
                    "data": credentials,
                    "updated_at": datetime.now().isoformat()
                }).eq("slack_id", slack_id).eq("credential_type", credential_type).execute()
            else:
                # Insert new credentials
                response = self.client.table("credentials").insert(cred_data).execute()
            
            if response.data:
                logger.info(f"Stored {credential_type} credentials for user {slack_id}")
                return response.data[0]
            else:
                logger.error(f"No data returned from Supabase credential storage for {slack_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error storing credentials in Supabase: {e}")
            return None
    
    def get_credentials(self, slack_id, credential_type):
        """Get user credentials from Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        
        try:
            response = self.client.table("credentials").select("*").eq("slack_id", slack_id).eq("credential_type", credential_type).execute()
            
            if response.data:
                return response.data[0].get("data")
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting credentials from Supabase: {e}")
            return None
    
    def log_interaction(self, slack_id, interaction_type, details=None):
        """Log an interaction with a user in Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        
        try:
            # Prepare interaction data
            interaction_data = {
                "slack_id": slack_id,
                "interaction_type": interaction_type,
                "details": details,
                "created_at": datetime.now().isoformat()
            }
            
            # Insert interaction
            response = self.client.table("interactions").insert(interaction_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                logger.error(f"No data returned from Supabase interaction logging for {slack_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error logging interaction in Supabase: {e}")
            return None
    
    def get_recent_interactions(self, slack_id, interaction_type=None, limit=10):
        """Get recent interactions with a user from Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return []
        
        try:
            # Build query
            query = self.client.table("interactions").select("*").eq("slack_id", slack_id)
            
            if interaction_type:
                query = query.eq("interaction_type", interaction_type)
            
            # Order by created_at desc and limit
            query = query.order("created_at", desc=True).limit(limit)
            
            # Execute query
            response = query.execute()
            
            if response.data:
                return response.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting interactions from Supabase: {e}")
            return []
    
    def get_all_users(self):
        """Get all users from Supabase"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return []
        
        try:
            response = self.client.table("users").select("*").execute()
            
            if response.data:
                return response.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting all users from Supabase: {e}")
            return []
