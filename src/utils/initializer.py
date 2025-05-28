import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import integrations
from ..integrations.slack_integration import SlackIntegration
from ..integrations.github_integration import GitHubIntegration
from ..integrations.google_calendar_integration import GoogleCalendarIntegration
from ..integrations.gmail_integration import GmailIntegration
from ..integrations.youtrack_integration import YouTrackIntegration
from ..integrations.supabase_integration import SupabaseIntegration

# Import utilities
from .user_manager import UserManager
from .activity_monitor import ActivityMonitor

logger = logging.getLogger(__name__)

class Initializer:
    """
    Initializes all components of the Slack bot.
    Ensures all necessary files, directories, and services are available.
    """
    
    def __init__(self):
        """Initialize the initializer"""
        # Load environment variables
        load_dotenv()
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize Supabase
        self.supabase = None
        
        # Initialize components
        self.user_manager = None
        self.activity_monitor = None
        self.slack = None
        self.github = None
        self.calendar = None
        self.gmail = None
        self.youtrack = None
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            "data",
            "logs"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def initialize_all(self):
        """Initialize all components"""
        logger.info("Initializing all components")
        
        # Initialize Supabase first
        self.supabase = self._initialize_supabase()
        
        # Initialize utilities
        self.user_manager = self._initialize_user_manager()
        self.activity_monitor = self._initialize_activity_monitor()
        
        # Initialize integrations
        self.slack = self._initialize_slack()
        self.github = self._initialize_github()
        self.calendar = self._initialize_calendar()
        self.gmail = self._initialize_gmail()
        self.youtrack = self._initialize_youtrack()
        
        logger.info("All components initialized")
        
        return {
            'supabase': self.supabase,
            'user_manager': self.user_manager,
            'activity_monitor': self.activity_monitor,
            'slack': self.slack,
            'github': self.github,
            'calendar': self.calendar,
            'gmail': self.gmail,
            'youtrack': self.youtrack
        }
        
    def _initialize_supabase(self):
        """Initialize Supabase and set up tables if needed"""
        try:
            logger.info("Initializing Supabase integration")
            
            # Check if required environment variables are set
            if not os.environ.get("SUPABASE_URL"):
                logger.warning("SUPABASE_URL not set in environment variables")
                return None
            
            if not os.environ.get("SUPABASE_KEY"):
                logger.warning("SUPABASE_KEY not set in environment variables")
                return None
            
            # Initialize Supabase client
            supabase = SupabaseIntegration()
            
            # Check if client was initialized successfully
            if not supabase.client:
                logger.error("Failed to initialize Supabase client")
                return None
            
            # Set up tables if they don't exist
            self._setup_supabase_tables(supabase)
            
            return supabase
        except Exception as e:
            logger.error(f"Error initializing Supabase: {e}")
            return None
    
    def _setup_supabase_tables(self, supabase):
        """Set up Supabase tables if they don't exist"""
        # This would typically be done with SQL migrations
        # For simplicity, we'll just check if tables exist and create them if not
        try:
            # We can't easily check if tables exist through the Python client
            # In a real implementation, you would use migrations or RPC functions
            # For now, we'll assume the tables are set up correctly
            logger.info("Supabase tables assumed to be set up correctly")
            
            # The required tables are:
            # - users: For storing user data
            # - credentials: For storing user credentials
            # - interactions: For logging user interactions
            
            return True
        except Exception as e:
            logger.error(f"Error setting up Supabase tables: {e}")
            return False
    
    def _initialize_user_manager(self):
        """Initialize the user manager"""
        try:
            logger.info("Initializing user manager with Supabase")
            # User manager now uses Supabase for storage
            return UserManager()
        except Exception as e:
            logger.error(f"Error initializing user manager: {e}")
            return None
    
    def _initialize_activity_monitor(self):
        """Initialize the activity monitor"""
        try:
            logger.info("Initializing activity monitor")
            return ActivityMonitor()
        except Exception as e:
            logger.error(f"Error initializing activity monitor: {e}")
            return None
    
    def _initialize_slack(self):
        """Initialize the Slack integration"""
        try:
            logger.info("Initializing Slack integration")
            
            # Check if required environment variables are set
            if not os.environ.get("SLACK_BOT_TOKEN"):
                logger.warning("SLACK_BOT_TOKEN not set in environment variables")
                return None
            
            if not os.environ.get("SLACK_SIGNING_SECRET"):
                logger.warning("SLACK_SIGNING_SECRET not set in environment variables")
                return None
            
            return SlackIntegration()
        except Exception as e:
            logger.error(f"Error initializing Slack integration: {e}")
            return None
    
    def _initialize_github(self):
        """Initialize the GitHub integration"""
        try:
            logger.info("Initializing GitHub integration")
            
            # Check if required environment variables are set
            if not os.environ.get("GITHUB_TOKEN"):
                logger.warning("GITHUB_TOKEN not set in environment variables")
                return None
            
            return GitHubIntegration()
        except Exception as e:
            logger.error(f"Error initializing GitHub integration: {e}")
            return None
    
    def _initialize_calendar(self):
        """Initialize the Google Calendar integration"""
        try:
            logger.info("Initializing Google Calendar integration")
            
            # Check if required environment variables are set
            if not os.environ.get("GOOGLE_CREDENTIALS_FILE"):
                logger.warning("GOOGLE_CREDENTIALS_FILE not set in environment variables")
                return None
            
            # Check if the credentials file exists
            credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE")
            if not os.path.exists(credentials_file):
                logger.warning(f"Google credentials file not found: {credentials_file}")
                return None
            
            return GoogleCalendarIntegration()
        except Exception as e:
            logger.error(f"Error initializing Google Calendar integration: {e}")
            return None
    
    def _initialize_gmail(self):
        """Initialize the Gmail integration"""
        try:
            logger.info("Initializing Gmail integration")
            
            # Check if required environment variables are set
            if not os.environ.get("GOOGLE_CREDENTIALS_FILE"):
                logger.warning("GOOGLE_CREDENTIALS_FILE not set in environment variables")
                return None
            
            # Check if the credentials file exists
            credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE")
            if not os.path.exists(credentials_file):
                logger.warning(f"Google credentials file not found: {credentials_file}")
                return None
            
            return GmailIntegration()
        except Exception as e:
            logger.error(f"Error initializing Gmail integration: {e}")
            return None
    
    def _initialize_youtrack(self):
        """Initialize the YouTrack integration"""
        try:
            logger.info("Initializing YouTrack integration")
            
            # Check if required environment variables are set
            if not os.environ.get("YOUTRACK_URL"):
                logger.warning("YOUTRACK_URL not set in environment variables")
                return None
            
            if not os.environ.get("YOUTRACK_TOKEN"):
                logger.warning("YOUTRACK_TOKEN not set in environment variables")
                return None
            
            return YouTrackIntegration()
        except Exception as e:
            logger.error(f"Error initializing YouTrack integration: {e}")
            return None
    
    def check_status(self):
        """Check the status of all components"""
        status = {
            'user_manager': self.user_manager is not None,
            'activity_monitor': self.activity_monitor is not None,
            'slack': self.slack is not None,
            'github': self.github is not None,
            'calendar': self.calendar is not None,
            'gmail': self.gmail is not None,
            'youtrack': self.youtrack is not None
        }
        
        return status
