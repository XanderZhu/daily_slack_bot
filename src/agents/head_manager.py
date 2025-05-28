import logging
import autogen
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HeadManagerAgent:
    """
    The Head Manager Agent coordinates all other agents in the network.
    It decides which agent should handle a specific request and manages the overall workflow.
    """
    
    def __init__(self, config_list):
        """Initialize the Head Manager Agent"""
        self.config_list = config_list
        self.agents = []
        self.components = {}
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="HeadManager",
            llm_config={"config_list": config_list},
            system_message="""You are the Head Manager Agent responsible for coordinating all other agents in the network.
            Your role is to analyze user requests, delegate tasks to appropriate specialized agents, and synthesize their responses.
            You should ensure a coherent and helpful experience for the user by managing the workflow between agents."""
        )
        
    def set_components(self, components):
        """Set external components for the agent to use"""
        self.components = components
    
    def register_agent(self, agent):
        """Register a new agent with the head manager"""
        self.agents.append(agent)
        logger.info(f"Registered agent: {agent.__class__.__name__}")
    
    def process_request(self, user_id, text):
        """Process a user request by delegating to appropriate agents"""
        logger.info(f"Processing request from user {user_id}: {text}")
        
        # Determine which agent(s) should handle this request
        relevant_agents = self._select_relevant_agents(text)
        
        # Collect responses from relevant agents
        responses = []
        for agent in relevant_agents:
            response = agent.process_request(user_id, text)
            responses.append(response)
        
        # Synthesize a coherent response
        final_response = self._synthesize_responses(responses, text)
        return final_response
    
    def _select_relevant_agents(self, text):
        """Select which agents are relevant for handling this request"""
        # Simple keyword-based routing for now
        relevant_agents = []
        
        keywords = {
            "plan": ["daily_planner"],
            "task": ["project_analyst", "daily_planner"],
            "help": ["motivator"],
            "code": ["developer_assistant"],
            "research": ["research_agent"],
            "meeting": ["communication_agent"],
            "email": ["communication_agent"],
            "github": ["developer_assistant", "project_analyst"],
            "youtrack": ["project_analyst"]
        }
        
        # Check for keywords in the text
        for keyword, agent_types in keywords.items():
            if keyword.lower() in text.lower():
                for agent_type in agent_types:
                    for agent in self.agents:
                        if agent.__class__.__name__.lower() == agent_type.lower():
                            if agent not in relevant_agents:
                                relevant_agents.append(agent)
        
        # If no specific agents were identified, include all agents
        if not relevant_agents:
            relevant_agents = self.agents
        
        return relevant_agents
    
    def _synthesize_responses(self, responses, original_text):
        """Synthesize multiple agent responses into a coherent reply"""
        if not responses:
            return "I'm not sure how to help with that. Could you provide more details?"
        
        if len(responses) == 1:
            return responses[0]
        
        # Use AutoGen to synthesize responses
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for the synthesis
        synthesis_prompt = f"""
        Original user request: {original_text}
        
        Agent responses:
        {' '.join(responses)}
        
        Synthesize these responses into a coherent, helpful reply that addresses the user's request.
        """
        
        # Get the synthesized response
        user_proxy.initiate_chat(
            self.agent,
            message=synthesis_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            return " ".join(responses)
    
    def generate_welcome_message(self, user_id):
        """Generate the daily welcome message with meetings and tasks"""
        # Check if user has completed onboarding
        user_manager = self.components.get('user_manager') if hasattr(self, 'components') else None
        if user_manager:
            user_data = user_manager.get_user(user_id)
            if not user_data.get('onboarding_completed', False):
                # User hasn't completed onboarding, return onboarding message instead
                return (
                    "Welcome to Daily Slack Bot! 👋\n\n"
                    "Before I can provide you with personalized assistance, I need to set up your account.\n"
                    "Let's start by connecting your work tools like GitHub, Google Calendar, and more.\n\n"
                    "Type anything to begin the setup process."
                )
        
        # Get calendar events from the communication agent
        calendar_agent = next((a for a in self.agents if a.__class__.__name__ == "CommunicationAgent"), None)
        meetings = calendar_agent.get_todays_meetings(user_id) if calendar_agent else []
        
        # Get tasks from the project analyst
        task_agent = next((a for a in self.agents if a.__class__.__name__ == "ProjectAnalystAgent"), None)
        tasks = task_agent.get_pending_tasks(user_id) if task_agent else []
        
        # Get planning assistance from the daily planner
        planner_agent = next((a for a in self.agents if a.__class__.__name__ == "DailyPlannerAgent"), None)
        planning_prompt = planner_agent.get_planning_prompt() if planner_agent else ""
        
        # Construct the welcome message
        welcome_message = f"Good morning! Here's your daily summary:\n\n"
        
        if meetings:
            welcome_message += "**Today's Meetings:**\n"
            for meeting in meetings:
                welcome_message += f"- {meeting['time']}: {meeting['title']}\n"
            welcome_message += "\n"
        else:
            welcome_message += "**Today's Meetings:** No meetings scheduled for today.\n\n"
        
        if tasks:
            welcome_message += "**Pending Tasks:**\n"
            for task in tasks:
                welcome_message += f"- {task['title']}\n"
            welcome_message += "\n"
        else:
            welcome_message += "**Pending Tasks:** No pending tasks found.\n\n"
        
        welcome_message += f"Let's plan what you'll do today! {planning_prompt}"
        
        return welcome_message
    
    def generate_hourly_checkin(self, user_id):
        """Generate an hourly check-in message"""
        return "How's your work going? Do you need any assistance with your current tasks?"
    
    def check_user_activity(self, user_id):
        """Check user activity and provide support if needed"""
        # Get activity data from relevant agents
        dev_agent = next((a for a in self.agents if a.__class__.__name__ == "DeveloperAssistantAgent"), None)
        github_activity = dev_agent.get_github_activity(user_id) if dev_agent else None
        
        # Determine if activity has decreased
        if github_activity and github_activity.get("decreased", False):
            # Get motivational support
            motivator_agent = next((a for a in self.agents if a.__class__.__name__ == "MotivatorAgent"), None)
            motivation = motivator_agent.generate_motivation(user_id) if motivator_agent else ""
            
            return f"I noticed your activity has decreased. {motivation} Would you like some help with your current tasks?"
        
        return None
