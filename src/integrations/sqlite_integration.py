import os
import logging
import sqlite3
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteIntegration:
    """Integration with SQLite for data storage"""
    
    def __init__(self, db_path=None):
        """Initialize SQLite database"""
        try:
            # Use the provided path or default to a data directory in the project
            if db_path is None:
                data_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data"
                data_dir.mkdir(exist_ok=True)
                db_path = data_dir / "slack_bot.db"
            
            self.db_path = str(db_path)
            logger.info(f"Initializing SQLite database at {self.db_path}")
            
            # Initialize database and create tables if they don't exist
            self._init_db()
            
            logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            self.conn = None
    
    def _init_db(self):
        """Initialize database and create tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Create tables if they don't exist
        cursor = self.conn.cursor()
        
        # Users table - create with basic columns first
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slack_id TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT,
            created_at TEXT,
            updated_at TEXT,
            preferences TEXT
        )
        ''')
        
        # Credentials table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slack_id TEXT NOT NULL,
            credential_type TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(slack_id, credential_type)
        )
        ''')
        
        # Interactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slack_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            details TEXT,
            created_at TEXT
        )
        ''')
        
        # Commit the basic tables
        self.conn.commit()
        
        # Now check for and add missing columns to the users table
        try:
            # Get existing columns in the users table
            cursor.execute("PRAGMA table_info(users)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            # Define the columns that should exist for onboarding
            required_columns = [
                ("onboarding_started", "BOOLEAN"),
                ("onboarding_completed", "BOOLEAN"),
                ("onboarding_step", "TEXT"),
                ("onboarding_timestamp", "TEXT"),
                ("onboarding_completion_timestamp", "TEXT"),
                ("github_setup", "TEXT"),
                ("google_setup", "TEXT"),
                ("youtrack_setup", "TEXT")
            ]
            
            # Add missing columns
            for column_name, column_type in required_columns:
                if column_name not in existing_columns:
                    logger.info(f"Adding column {column_name} to users table")
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
            
            # Commit the column additions
            self.conn.commit()
            logger.info("Database schema updated successfully")
        except Exception as e:
            logger.error(f"Error updating database schema: {e}")
            # Continue anyway - the basic functionality should still work
    
    def get_user(self, slack_id):
        """Get user data from SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return None
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE slack_id = ?", (slack_id,))
            user = cursor.fetchone()
            
            if user:
                # Convert to dictionary
                user_dict = dict(user)
                
                # Parse JSON fields
                if user_dict.get('preferences'):
                    user_dict['preferences'] = json.loads(user_dict['preferences'])
                
                return user_dict
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting user from SQLite: {e}")
            return None
    
    def create_user(self, user_data):
        """Create a new user in SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return None
            
        try:
            # Ensure required fields
            if 'slack_id' not in user_data:
                logger.error("slack_id is required to create a user")
                return None
            
            # Set timestamps if not provided
            now = datetime.now().isoformat()
            if 'created_at' not in user_data:
                user_data['created_at'] = now
            if 'updated_at' not in user_data:
                user_data['updated_at'] = now
            
            # Handle JSON fields
            if 'preferences' in user_data and not isinstance(user_data['preferences'], str):
                user_data['preferences'] = json.dumps(user_data['preferences'])
            
            # Prepare data for insertion
            fields = []
            values = []
            placeholders = []
            
            for key, value in user_data.items():
                fields.append(key)
                values.append(value)
                placeholders.append('?')
            
            # Create SQL query
            query = f"INSERT INTO users ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            
            # Execute query
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()
            
            # Return the created user
            return self.get_user(user_data['slack_id'])
        except Exception as e:
            logger.error(f"Error creating user in SQLite: {e}")
            return None
    
    def update_user(self, slack_id, user_data):
        """Update user data in SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return None
            
        try:
            # Set updated_at timestamp
            user_data['updated_at'] = datetime.now().isoformat()
            
            # Handle JSON fields
            if 'preferences' in user_data and not isinstance(user_data['preferences'], str):
                user_data['preferences'] = json.dumps(user_data['preferences'])
            
            # Prepare data for update
            set_clauses = []
            values = []
            
            for key, value in user_data.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            # Add slack_id to values
            values.append(slack_id)
            
            # Create SQL query
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE slack_id = ?"
            
            # Execute query
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()
            
            # Return the updated user
            return self.get_user(slack_id)
        except Exception as e:
            logger.error(f"Error updating user in SQLite: {e}")
            return None
    
    def store_credentials(self, slack_id, credential_type, credentials):
        """Store user credentials in SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return None
        
        try:
            now = datetime.now().isoformat()
            
            # Convert credentials to JSON string if needed
            if not isinstance(credentials, str):
                credentials = json.dumps(credentials)
            
            # Check if credentials already exist
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM credentials WHERE slack_id = ? AND credential_type = ?",
                (slack_id, credential_type)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing credentials
                cursor.execute(
                    "UPDATE credentials SET data = ?, updated_at = ? WHERE slack_id = ? AND credential_type = ?",
                    (credentials, now, slack_id, credential_type)
                )
            else:
                # Insert new credentials
                cursor.execute(
                    "INSERT INTO credentials (slack_id, credential_type, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (slack_id, credential_type, credentials, now, now)
                )
            
            self.conn.commit()
            
            # Return the stored credentials
            return {
                "slack_id": slack_id,
                "credential_type": credential_type,
                "data": credentials if isinstance(credentials, dict) else json.loads(credentials),
                "updated_at": now
            }
        except Exception as e:
            logger.error(f"Error storing credentials in SQLite: {e}")
            return None
    
    def get_credentials(self, slack_id, credential_type):
        """Get user credentials from SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return None
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM credentials WHERE slack_id = ? AND credential_type = ?",
                (slack_id, credential_type)
            )
            cred = cursor.fetchone()
            
            if cred:
                # Parse JSON data
                data = cred['data']
                return json.loads(data) if data else None
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting credentials from SQLite: {e}")
            return None
    
    def log_interaction(self, slack_id, interaction_type, details=None):
        """Log an interaction with a user in SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return None
        
        try:
            now = datetime.now().isoformat()
            
            # Convert details to JSON string if needed
            if details and not isinstance(details, str):
                details = json.dumps(details)
            
            # Insert interaction
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO interactions (slack_id, interaction_type, details, created_at) VALUES (?, ?, ?, ?)",
                (slack_id, interaction_type, details, now)
            )
            
            self.conn.commit()
            
            # Return the logged interaction
            return {
                "id": cursor.lastrowid,
                "slack_id": slack_id,
                "interaction_type": interaction_type,
                "details": details if isinstance(details, dict) else (json.loads(details) if details else None),
                "created_at": now
            }
        except Exception as e:
            logger.error(f"Error logging interaction in SQLite: {e}")
            return None
    
    def get_recent_interactions(self, slack_id, interaction_type=None, limit=10):
        """Get recent interactions with a user from SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return []
        
        try:
            cursor = self.conn.cursor()
            
            if interaction_type:
                cursor.execute(
                    "SELECT * FROM interactions WHERE slack_id = ? AND interaction_type = ? ORDER BY created_at DESC LIMIT ?",
                    (slack_id, interaction_type, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM interactions WHERE slack_id = ? ORDER BY created_at DESC LIMIT ?",
                    (slack_id, limit)
                )
            
            interactions = cursor.fetchall()
            
            # Convert to list of dictionaries and parse JSON
            result = []
            for interaction in interactions:
                interaction_dict = dict(interaction)
                
                # Parse JSON details
                if interaction_dict.get('details'):
                    try:
                        interaction_dict['details'] = json.loads(interaction_dict['details'])
                    except:
                        pass  # Keep as string if not valid JSON
                
                result.append(interaction_dict)
            
            return result
        except Exception as e:
            logger.error(f"Error getting interactions from SQLite: {e}")
            return []
    
    def get_all_users(self):
        """Get all users from SQLite"""
        if not self.conn:
            logger.error("SQLite database not initialized")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            # Convert to list of dictionaries and parse JSON
            result = []
            for user in users:
                user_dict = dict(user)
                
                # Parse JSON fields
                if user_dict.get('preferences'):
                    try:
                        user_dict['preferences'] = json.loads(user_dict['preferences'])
                    except:
                        pass  # Keep as string if not valid JSON
                
                result.append(user_dict)
            
            return result
        except Exception as e:
            logger.error(f"Error getting all users from SQLite: {e}")
            return []
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
