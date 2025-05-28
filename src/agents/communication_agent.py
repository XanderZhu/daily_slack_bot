import logging
import autogen
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CommunicationAgent:
    """
    The Communication Agent helps with meetings and messages.
    It assists with scheduling, drafting communications, and managing calendar events.
    """
    
    def __init__(self, config_list):
        """Initialize the Communication Agent"""
        self.config_list = config_list
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="CommunicationAgent",
            llm_config={"config_list": config_list},
            system_message="""You are the Communication Agent responsible for helping with meetings and messages.
            Your role is to assist users with scheduling meetings, drafting emails and messages,
            and managing calendar events. You should help users communicate effectively,
            maintain a well-organized calendar, and ensure important information is conveyed clearly."""
        )
    
    def process_request(self, user_id, text):
        """Process a communication-related request"""
        logger.info(f"Communication Agent processing request from user {user_id}")
        
        # Use AutoGen to generate a response
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for communication assistance
        communication_prompt = f"""
        User request: {text}
        
        Analyze this request and provide communication assistance. Consider:
        1. Understanding the communication need (scheduling, drafting, etc.)
        2. Identifying key information to include
        3. Suggesting appropriate tone and format
        4. Providing clear, well-structured content
        5. Ensuring all necessary details are included
        
        Respond with helpful communication assistance.
        """
        
        # Get the communication response
        user_proxy.initiate_chat(
            self.agent,
            message=communication_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            return "I can help you with scheduling meetings or drafting messages. What specific communication task would you like assistance with?"
    
    def get_todays_meetings(self, user_id):
        """Get today's meetings from the user's calendar"""
        # This would connect to the Google Calendar API
        # For now, return sample data
        
        # Get current date
        today = datetime.now().strftime("%Y-%m-%d")
        
        return [
            {
                "id": "meeting1",
                "title": "Daily Standup",
                "time": "09:30",
                "duration": 30,
                "attendees": ["team@example.com"],
                "location": "Virtual - Zoom"
            },
            {
                "id": "meeting2",
                "title": "Project Planning",
                "time": "11:00",
                "duration": 60,
                "attendees": ["manager@example.com", "team@example.com"],
                "location": "Conference Room A"
            },
            {
                "id": "meeting3",
                "title": "Client Demo",
                "time": "15:00",
                "duration": 45,
                "attendees": ["client@example.com", "sales@example.com"],
                "location": "Virtual - Teams"
            }
        ]
    
    def schedule_meeting(self, title, attendees, duration, preferred_times=None):
        """Schedule a meeting on the user's calendar"""
        # This would connect to the Google Calendar API
        # For now, return a sample response
        
        # Generate a sample meeting time
        now = datetime.now()
        meeting_time = now + timedelta(days=1, hours=2)
        meeting_time = meeting_time.replace(minute=0, second=0, microsecond=0)
        
        return {
            "success": True,
            "meeting": {
                "id": "new_meeting",
                "title": title,
                "time": meeting_time.strftime("%Y-%m-%d %H:%M"),
                "duration": duration,
                "attendees": attendees,
                "location": "Virtual - Zoom"
            }
        }
    
    def draft_email(self, recipient, subject, key_points):
        """Draft an email based on provided information"""
        # Use AutoGen to generate an email draft
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for email drafting
        email_prompt = f"""
        Draft an email with the following details:
        Recipient: {recipient}
        Subject: {subject}
        Key points to include:
        {' '.join([f"- {point}" for point in key_points])}
        
        Please draft a professional, clear email that covers all the key points.
        The tone should be professional but friendly, and the email should be well-structured.
        Include an appropriate greeting and sign-off.
        """
        
        # Get the email draft response
        user_proxy.initiate_chat(
            self.agent,
            message=email_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback email draft if AutoGen fails
            email_draft = f"""
            Subject: {subject}
            
            Dear {recipient},
            
            I hope this email finds you well.
            
            """
            
            for point in key_points:
                email_draft += f"{point}\n\n"
            
            email_draft += """
            Please let me know if you have any questions or need further information.
            
            Best regards,
            [Your Name]
            """
            
            return email_draft
    
    def draft_slack_message(self, channel, purpose, key_points):
        """Draft a Slack message based on provided information"""
        # Use AutoGen to generate a Slack message draft
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for Slack message drafting
        slack_prompt = f"""
        Draft a Slack message with the following details:
        Channel: {channel}
        Purpose: {purpose}
        Key points to include:
        {' '.join([f"- {point}" for point in key_points])}
        
        Please draft a clear, concise Slack message that covers all the key points.
        The tone should be appropriate for team communication in Slack (more casual than email but still professional).
        Format the message appropriately for Slack, using formatting like bold or bullet points where helpful.
        """
        
        # Get the Slack message draft response
        user_proxy.initiate_chat(
            self.agent,
            message=slack_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback Slack message draft if AutoGen fails
            slack_draft = f"*{purpose}*\n\n"
            
            for point in key_points:
                slack_draft += f"• {point}\n"
            
            return slack_draft
    
    def find_meeting_time(self, attendees, duration, date_range):
        """Find available meeting times for a group of attendees"""
        # This would connect to the Google Calendar API to check availability
        # For now, return sample data
        
        start_date = datetime.now()
        if isinstance(date_range, list) and len(date_range) >= 2:
            start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
        
        available_slots = []
        
        # Generate some sample time slots
        for i in range(3):
            slot_date = start_date + timedelta(days=i)
            
            # Morning slot
            morning_slot = {
                "date": slot_date.strftime("%Y-%m-%d"),
                "start_time": "10:00",
                "end_time": "10:30" if duration <= 30 else "11:00",
                "available_attendees": attendees
            }
            available_slots.append(morning_slot)
            
            # Afternoon slot
            afternoon_slot = {
                "date": slot_date.strftime("%Y-%m-%d"),
                "start_time": "14:00",
                "end_time": "14:30" if duration <= 30 else "15:00",
                "available_attendees": attendees
            }
            available_slots.append(afternoon_slot)
        
        # Format the available slots as a readable response
        response = f"Here are some available meeting times ({duration} minutes):\n\n"
        
        for slot in available_slots:
            response += f"**{slot['date']} from {slot['start_time']} to {slot['end_time']}**\n"
            response += f"All attendees are available.\n\n"
        
        return response
