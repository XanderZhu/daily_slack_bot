import logging
import autogen
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DailyPlannerAgent:
    """
    The Daily Planner Agent helps users plan their day effectively.
    It provides suggestions for organizing tasks and managing time.
    """
    
    def __init__(self, config_list):
        """Initialize the Daily Planner Agent"""
        self.config_list = config_list
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="DailyPlanner",
            llm_config={"config_list": config_list},
            system_message="""You are the Daily Planner Agent responsible for helping users plan their workday effectively.
            Your role is to analyze tasks, meetings, and priorities to suggest optimal schedules and time management strategies.
            You should provide practical advice for organizing work, setting priorities, and maintaining productivity."""
        )
    
    def process_request(self, user_id, text):
        """Process a planning-related request"""
        logger.info(f"Daily Planner processing request from user {user_id}")
        
        # Use AutoGen to generate a response
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for planning
        planning_prompt = f"""
        User request: {text}
        
        Analyze this request and provide helpful planning advice. Consider:
        1. How to prioritize tasks effectively
        2. Time management strategies
        3. Balancing meetings and focused work time
        4. Breaking down complex tasks into manageable steps
        
        Respond with practical, actionable planning advice.
        """
        
        # Get the planning response
        user_proxy.initiate_chat(
            self.agent,
            message=planning_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            return "I can help you plan your day more effectively. What specific aspects would you like assistance with?"
    
    def get_planning_prompt(self):
        """Get a prompt to encourage daily planning"""
        planning_prompts = [
            "What are your top priorities for today?",
            "How would you like to organize your tasks for maximum productivity?",
            "What's the most important thing you want to accomplish today?",
            "Would you like help breaking down your day into manageable chunks?",
            "Let's prioritize your tasks and create a schedule that works for you."
        ]
        
        import random
        return random.choice(planning_prompts)
    
    def suggest_daily_plan(self, user_id, tasks, meetings):
        """Suggest a daily plan based on tasks and meetings"""
        # Organize tasks by priority
        high_priority = [t for t in tasks if t.get("priority") == "high"]
        medium_priority = [t for t in tasks if t.get("priority") == "medium"]
        low_priority = [t for t in tasks if t.get("priority") == "low"]
        
        # Sort meetings by time
        sorted_meetings = sorted(meetings, key=lambda x: x.get("time", ""))
        
        # Create time blocks around meetings
        schedule = []
        current_time = "09:00"  # Assuming workday starts at 9 AM
        
        for meeting in sorted_meetings:
            meeting_time = meeting.get("time", "")
            meeting_duration = meeting.get("duration", 60)  # Default to 60 minutes
            
            # Add a work block before the meeting if there's time
            if meeting_time > current_time:
                work_block = {
                    "start_time": current_time,
                    "end_time": meeting_time,
                    "activity": "Focus Work",
                    "tasks": []
                }
                
                # Assign tasks to this work block
                remaining_time = self._calculate_time_difference(current_time, meeting_time)
                assigned_tasks = self._assign_tasks_to_block(high_priority + medium_priority, remaining_time)
                work_block["tasks"] = assigned_tasks
                
                schedule.append(work_block)
            
            # Add the meeting block
            meeting_end_time = self._add_minutes_to_time(meeting_time, meeting_duration)
            meeting_block = {
                "start_time": meeting_time,
                "end_time": meeting_end_time,
                "activity": "Meeting",
                "meeting": meeting.get("title", "Untitled Meeting")
            }
            schedule.append(meeting_block)
            
            current_time = meeting_end_time
        
        # Add a final work block if the day isn't over
        if current_time < "17:00":  # Assuming workday ends at 5 PM
            work_block = {
                "start_time": current_time,
                "end_time": "17:00",
                "activity": "Focus Work",
                "tasks": []
            }
            
            # Assign remaining tasks to this work block
            remaining_time = self._calculate_time_difference(current_time, "17:00")
            assigned_tasks = self._assign_tasks_to_block(
                high_priority + medium_priority + low_priority, 
                remaining_time
            )
            work_block["tasks"] = assigned_tasks
            
            schedule.append(work_block)
        
        # Format the schedule as a readable plan
        plan = "Here's a suggested plan for your day:\n\n"
        
        for block in schedule:
            if block.get("activity") == "Meeting":
                plan += f"**{block['start_time']} - {block['end_time']}: {block['meeting']}**\n"
            else:
                plan += f"**{block['start_time']} - {block['end_time']}: Focus Work**\n"
                if block.get("tasks"):
                    for task in block["tasks"]:
                        plan += f"- {task['title']}\n"
                else:
                    plan += "- No specific tasks assigned\n"
            plan += "\n"
        
        return plan
    
    def _calculate_time_difference(self, start_time, end_time):
        """Calculate the difference between two times in minutes"""
        # Simple implementation for the example
        # In a real implementation, use datetime
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))
        
        start_minutes = start_hour * 60 + start_minute
        end_minutes = end_hour * 60 + end_minute
        
        return max(0, end_minutes - start_minutes)
    
    def _add_minutes_to_time(self, time_str, minutes):
        """Add minutes to a time string and return the new time"""
        # Simple implementation for the example
        # In a real implementation, use datetime
        hour, minute = map(int, time_str.split(":"))
        
        total_minutes = hour * 60 + minute + minutes
        new_hour = (total_minutes // 60) % 24
        new_minute = total_minutes % 60
        
        return f"{new_hour:02d}:{new_minute:02d}"
    
    def _assign_tasks_to_block(self, tasks, available_minutes):
        """Assign tasks to a time block based on estimated duration"""
        assigned_tasks = []
        remaining_minutes = available_minutes
        
        for task in tasks:
            task_duration = task.get("estimated_minutes", 30)  # Default to 30 minutes
            
            if task_duration <= remaining_minutes:
                assigned_tasks.append(task)
                remaining_minutes -= task_duration
            
            if remaining_minutes <= 0:
                break
        
        return assigned_tasks
