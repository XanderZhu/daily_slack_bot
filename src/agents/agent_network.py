import os
import autogen
from dotenv import load_dotenv
from .head_manager import HeadManagerAgent
from .daily_planner import DailyPlannerAgent
from .project_analyst import ProjectAnalystAgent
from .motivator import MotivatorAgent
from .developer_assistant import DeveloperAssistantAgent
from .research_agent import ResearchAgent
from .communication_agent import CommunicationAgent

# Load environment variables
load_dotenv()

class AgentNetwork:
    """
    Manages the network of AutoGen agents for the Slack bot.
    Coordinates communication between agents and handles user interactions.
    """
    
    def __init__(self):
        """Initialize the agent network with all required agents"""
        # Configure LLM settings
        config_list = [
            {
                "model": os.environ.get("LITELLM_MODEL"),
                "api_key": os.environ.get("LITELLM_API_KEY"),
                "base_url": os.environ.get("LITELLM_BASE_URL"),
            }
        ]
        
        # Create the agents
        self.head_manager = HeadManagerAgent(config_list)
        self.daily_planner = DailyPlannerAgent(config_list)
        self.project_analyst = ProjectAnalystAgent(config_list)
        self.motivator = MotivatorAgent(config_list)
        self.developer_assistant = DeveloperAssistantAgent(config_list)
        self.research_agent = ResearchAgent(config_list)
        self.communication_agent = CommunicationAgent(config_list)
        
        # External components
        self.components = {}
        
        # Set up the agent network connections
        self._setup_network()
        
    def set_components(self, components):
        """Set external components for the agent network to use"""
        self.components = components
        
        # Make components available to individual agents if needed
        for agent in [self.head_manager, self.daily_planner, self.project_analyst, 
                     self.motivator, self.developer_assistant, self.research_agent, 
                     self.communication_agent]:
            if hasattr(agent, 'set_components'):
                agent.set_components(components)
        
    def _setup_network(self):
        """Set up the connections between agents in the network"""
        # Register agents with the head manager
        self.head_manager.register_agent(self.daily_planner)
        self.head_manager.register_agent(self.project_analyst)
        self.head_manager.register_agent(self.motivator)
        self.head_manager.register_agent(self.developer_assistant)
        self.head_manager.register_agent(self.research_agent)
        self.head_manager.register_agent(self.communication_agent)
    
    def process_mention(self, user_id, text):
        """Process a mention of the bot in a channel"""
        return self.head_manager.process_request(user_id, text)
    
    def process_direct_message(self, user_id, text):
        """Process a direct message to the bot"""
        return self.head_manager.process_request(user_id, text)
    
    def send_welcome_message(self, user_id):
        """Send the daily welcome message with meetings and tasks"""
        return self.head_manager.generate_welcome_message(user_id)
    
    def send_hourly_checkin(self, user_id):
        """Send an hourly check-in message to the user"""
        return self.head_manager.generate_hourly_checkin(user_id)
    
    def check_activity(self, user_id):
        """Check user activity and send support if needed"""
        return self.head_manager.check_user_activity(user_id)

def create_agent_network():
    """Create and return an instance of the agent network"""
    return AgentNetwork()
