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
            'user_manager': self.user_manager,
            'activity_monitor': self.activity_monitor,
            'slack': self.slack,
            'github': self.github,
            'calendar': self.calendar,
            'gmail': self.gmail,
            'youtrack': self.youtrack
        }
    
    def _initialize_user_manager(self):
        """Initialize the user manager"""
        try:
            logger.info("Initializing user manager")
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
