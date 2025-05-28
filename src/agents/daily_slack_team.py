import os
from typing import List, Dict, Any
import autogen
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from openai import OpenAI

# Initialize OpenAI client if API key is available
api_key = os.environ.get("LITELLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("LITELLM_BASE_URL")

if api_key:
    client = OpenAI(api_key=api_key, base_url=base_url)
else:
    client = None
    print("Warning: No API key found for OpenAI client. Set LITELLM_API_KEY or OPENAI_API_KEY environment variable.")

class TaskItem(BaseModel):
    """Model for a task item"""
    title: str
    description: str = ""
    priority: str = "Medium"
    due_date: str = ""
    status: str = "Pending"

class MeetingItem(BaseModel):
    """Model for a meeting item"""
    title: str
    time: str
    duration: int
    attendees: List[str]
    location: str = ""

class DailySlackTeam():
    """
    The Daily Slack Team implements a network of AutoGen agents for the Slack bot.
    It coordinates communication between agents and handles user interactions.
    """
    
    def __init__(self):
        self.feature_name = "daily_slack_bot"
        self.components = {}
    
    def set_components(self, components):
        """Set external components for the agent team to use"""
        self.components = components
    
    async def invoke(
        self, user_id: str, text: str, request_type: str = "direct_message"
    ):
        """
        Main entry point for the agent team
        
        Args:
            user_id: The user ID of the requester
            text: The text of the request
            request_type: The type of request (direct_message, mention, welcome, checkin)
        
        Returns:
            The response from the agent team
        """
        if request_type == "welcome":
            return await self.generate_welcome_message(user_id)
        elif request_type == "checkin":
            return await self.generate_hourly_checkin(user_id)
        elif request_type == "activity_check":
            return await self.check_user_activity(user_id)
        else:
            return await self.process_user_request(user_id, text)
    
    async def process_user_request(self, user_id: str, text: str):
        """Process a user request by delegating to the appropriate agents"""
        # Configure LLM settings
        llm_config = {
            "model": "gemini/gemini-2.5-flash-preview-04-17",
            "api_key": os.environ.get("LITELLM_API_KEY"),
            "base_url": os.environ.get("LITELLM_BASE_URL"),
            "stream": False,
        }
        
        # Create the agents
        head_manager = autogen.AssistantAgent(
            name="HeadManager",
            llm_config=llm_config,
            system_message="""You are the Head Manager Agent responsible for coordinating all other agents in the network.
            Your role is to analyze user requests, delegate tasks to appropriate specialized agents, and synthesize their responses.
            You should ensure a coherent and helpful experience for the user by managing the workflow between agents."""
        )
        
        daily_planner = autogen.AssistantAgent(
            name="DailyPlanner",
            llm_config=llm_config,
            system_message="""You are the Daily Planner Agent responsible for helping users plan their day.
            Your role is to assist with time management, task prioritization, and creating effective daily schedules.
            You should help users organize their tasks, allocate time efficiently, and maintain a productive workflow."""
        )
        
        project_analyst = autogen.AssistantAgent(
            name="ProjectAnalyst",
            llm_config=llm_config,
            system_message="""You are the Project Analyst Agent responsible for analyzing and managing complex projects.
            Your role is to help break down complex tasks, identify dependencies, and create structured project plans.
            You should assist with project management, issue tracking, and task decomposition."""
        )
        
        motivator = autogen.AssistantAgent(
            name="Motivator",
            llm_config=llm_config,
            system_message="""You are the Motivator Agent responsible for providing psychological support and motivation.
            Your role is to help users overcome challenges, maintain motivation, and manage stress.
            You should provide encouragement, emotional support, and strategies for maintaining well-being."""
        )
        
        developer_assistant = autogen.AssistantAgent(
            name="DeveloperAssistant",
            llm_config=llm_config,
            system_message="""You are the Developer Assistant Agent responsible for helping with coding tasks.
            Your role is to assist with code reviews, debugging, development best practices, and technical implementation.
            You should provide coding guidance, help solve technical problems, and support software development workflows."""
        )
        
        research_agent = autogen.AssistantAgent(
            name="ResearchAgent",
            llm_config=llm_config,
            system_message="""You are the Research Agent responsible for gathering and analyzing information.
            Your role is to help users find relevant information, summarize research findings, and provide insights.
            You should assist with information gathering, data analysis, and knowledge synthesis."""
        )
        
        communication_agent = autogen.AssistantAgent(
            name="CommunicationAgent",
            llm_config=llm_config,
            system_message="""You are the Communication Agent responsible for helping with meetings and messages.
            Your role is to assist users with scheduling meetings, drafting emails and messages,
            and managing calendar events. You should help users communicate effectively,
            maintain a well-organized calendar, and ensure important information is conveyed clearly."""
        )
        
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            code_execution_config=False,
        )
        
        def autogen_selector(last_speaker, groupchat):
            """
            Routes turns as:
            - first turn → head_manager
            - head_manager → appropriate specialist agent based on request
            - specialist agent → head_manager for synthesis
            - head_manager → user (final response)
            """
            # Get the agents in the same order they were added to the GroupChat
            agents = groupchat.agents
            head_manager_agent = agents[0]
            
            # First turn goes to head manager
            if last_speaker is None or last_speaker is user_proxy:
                return head_manager_agent
            
            # If head manager just spoke, determine which specialist to route to
            if last_speaker is head_manager_agent:
                # Extract the last message to determine which specialist to use
                last_message = groupchat.messages[-1]["content"].lower()
                
                # Simple keyword routing
                if "plan" in last_message or "schedule" in last_message:
                    return daily_planner
                elif "project" in last_message or "complex task" in last_message:
                    return project_analyst
                elif "motivation" in last_message or "support" in last_message:
                    return motivator
                elif "code" in last_message or "development" in last_message:
                    return developer_assistant
                elif "research" in last_message or "information" in last_message:
                    return research_agent
                elif "meeting" in last_message or "email" in last_message:
                    return communication_agent
                else:
                    # Default to the daily planner if no specific keywords match
                    return daily_planner
            
            # If a specialist just spoke, route back to head manager for synthesis
            if last_speaker in [daily_planner, project_analyst, motivator, 
                               developer_assistant, research_agent, communication_agent]:
                return head_manager_agent
            
            # Default case - stop the conversation
            return None
        
        # Create the group chat
        groupchat = autogen.GroupChat(
            agents=[head_manager, daily_planner, project_analyst, motivator, 
                   developer_assistant, research_agent, communication_agent, user_proxy],
            messages=[],
            speaker_selection_method="round_robin",  # Use a standard method first
            max_round=10
        )
        
        # Then override the select_speaker method with our custom selector
        groupchat.select_speaker = lambda last_speaker, manager=None: autogen_selector(last_speaker, groupchat)
        
        # Create the group chat manager
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config,
        )
        
        # Start the conversation
        user_message = f"User request: {text}\n\nPlease analyze this request and provide a helpful response."
        user_proxy.initiate_chat(
            manager,
            message=user_message,
            max_rounds=10
        )
        
        # Extract the final response from the head manager
        head_manager_messages = [m for m in groupchat.messages if m["name"] == head_manager.name]
        if head_manager_messages:
            return head_manager_messages[-1]["content"]
        else:
            return "I'm sorry, I wasn't able to process your request properly. Could you please try again?"
    
    async def generate_welcome_message(self, user_id):
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
        
        # Get today's meetings (mock data for now)
        meetings = self.get_todays_meetings(user_id)
        
        # Get pending tasks (mock data for now)
        tasks = self.get_pending_tasks(user_id)
        
        # Construct the welcome message
        welcome_message = f"Good morning! Here's your daily summary:\n\n"
        
        if meetings:
            welcome_message += "**Today's Meetings:**\n"
            for meeting in meetings:
                welcome_message += f"- {meeting.time}: {meeting.title}\n"
            welcome_message += "\n"
        else:
            welcome_message += "**Today's Meetings:** No meetings scheduled for today.\n\n"
        
        if tasks:
            welcome_message += "**Pending Tasks:**\n"
            for task in tasks:
                welcome_message += f"- {task.title}\n"
            welcome_message += "\n"
        else:
            welcome_message += "**Pending Tasks:** No pending tasks found.\n\n"
        
        welcome_message += "Let's plan what you'll do today! Would you like me to help you organize your tasks and schedule?"
        
        return welcome_message
    
    async def generate_hourly_checkin(self, user_id):
        """Generate an hourly check-in message"""
        return "How's your work going? Do you need any assistance with your current tasks?"
    
    async def check_user_activity(self, user_id):
        """Check user activity and provide support if needed"""
        # This would connect to GitHub API to check activity
        # For now, return a sample response
        github_activity = self.get_github_activity(user_id)
        
        # Determine if activity has decreased
        if github_activity and github_activity.get("decreased", False):
            return "I noticed your activity has decreased. Would you like some help with your current tasks or some motivation to get back on track?"
        
        return None
    
    def get_todays_meetings(self, user_id):
        """Get today's meetings from the user's calendar"""
        # This would connect to the Google Calendar API
        # For now, return sample data
        return [
            MeetingItem(
                title="Daily Standup",
                time="09:30",
                duration=30,
                attendees=["team@example.com"],
                location="Virtual - Zoom"
            ),
            MeetingItem(
                title="Project Planning",
                time="11:00",
                duration=60,
                attendees=["manager@example.com", "team@example.com"],
                location="Conference Room A"
            ),
            MeetingItem(
                title="Client Demo",
                time="15:00",
                duration=45,
                attendees=["client@example.com", "sales@example.com"],
                location="Virtual - Teams"
            )
        ]
    
    def get_pending_tasks(self, user_id):
        """Get pending tasks for the user"""
        # This would connect to GitHub/YouTrack API
        # For now, return sample data
        return [
            TaskItem(
                title="Implement new feature",
                description="Add user authentication to the application",
                priority="High",
                due_date="2025-05-30"
            ),
            TaskItem(
                title="Fix bug in reporting module",
                description="Reports are not showing correct data for last month",
                priority="Medium",
                due_date="2025-05-29"
            ),
            TaskItem(
                title="Review pull request",
                description="Review PR #123 from team member",
                priority="Low",
                due_date="2025-05-28"
            )
        ]
    
    def get_github_activity(self, user_id):
        """Get GitHub activity for the user"""
        # This would connect to GitHub API
        # For now, return sample data
        return {
            "commits_today": 2,
            "commits_yesterday": 5,
            "pull_requests_open": 1,
            "issues_assigned": 3,
            "decreased": True  # Sample data showing decreased activity
        }

def create_daily_slack_team():
    """Create and return an instance of the Daily Slack Team"""
    return DailySlackTeam()
