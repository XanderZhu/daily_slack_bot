import logging
import autogen
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ProjectAnalystAgent:
    """
    The Project Analyst Agent helps decompose complex tasks into manageable subtasks.
    It analyzes project requirements and provides structured breakdowns.
    """
    
    def __init__(self, config_list):
        """Initialize the Project Analyst Agent"""
        self.config_list = config_list
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="ProjectAnalyst",
            llm_config={"config_list": config_list},
            system_message="""You are the Project Analyst Agent responsible for helping users decompose complex tasks.
            Your role is to analyze project requirements, break down complex tasks into manageable subtasks,
            and help users organize their work effectively. You should provide structured approaches to tackling
            complex problems and help identify dependencies between tasks."""
        )
    
    def process_request(self, user_id, text):
        """Process a task decomposition request"""
        logger.info(f"Project Analyst processing request from user {user_id}")
        
        # Use AutoGen to generate a response
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for task analysis
        analysis_prompt = f"""
        User request: {text}
        
        Analyze this request and help decompose any complex tasks mentioned. Consider:
        1. Breaking down the task into smaller, manageable subtasks
        2. Identifying dependencies between subtasks
        3. Suggesting a logical order for completing the subtasks
        4. Estimating effort for each subtask
        5. Identifying potential challenges or blockers
        
        Respond with a structured task breakdown.
        """
        
        # Get the analysis response
        user_proxy.initiate_chat(
            self.agent,
            message=analysis_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            return "I can help you break down complex tasks into manageable steps. What specific project or task would you like me to analyze?"
    
    def get_pending_tasks(self, user_id):
        """Get pending tasks for a user from GitHub and YouTrack"""
        # This would connect to the GitHub and YouTrack APIs
        # For now, return sample data
        return [
            {
                "id": "TASK-1",
                "title": "Implement user authentication",
                "source": "GitHub",
                "priority": "high",
                "estimated_minutes": 120
            },
            {
                "id": "TASK-2",
                "title": "Fix navigation bug",
                "source": "GitHub",
                "priority": "medium",
                "estimated_minutes": 60
            },
            {
                "id": "TASK-3",
                "title": "Update documentation",
                "source": "YouTrack",
                "priority": "low",
                "estimated_minutes": 45
            }
        ]
    
    def decompose_task(self, task_description):
        """Decompose a complex task into subtasks"""
        # Use AutoGen to generate a task decomposition
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for task decomposition
        decomposition_prompt = f"""
        Task description: {task_description}
        
        Please decompose this task into smaller, manageable subtasks. For each subtask:
        1. Provide a clear title
        2. Add a brief description
        3. Estimate the effort required (in hours or story points)
        4. Identify any dependencies on other subtasks
        5. Suggest an appropriate assignee role (developer, designer, etc.)
        
        Format the response as a structured list of subtasks.
        """
        
        # Get the decomposition response
        user_proxy.initiate_chat(
            self.agent,
            message=decomposition_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback decomposition if AutoGen fails
            subtasks = [
                {
                    "title": "Research and Planning",
                    "description": "Research existing solutions and plan implementation approach",
                    "effort": "2 hours",
                    "dependencies": None,
                    "assignee_role": "Lead Developer"
                },
                {
                    "title": "Implementation",
                    "description": "Implement the core functionality",
                    "effort": "4 hours",
                    "dependencies": ["Research and Planning"],
                    "assignee_role": "Developer"
                },
                {
                    "title": "Testing",
                    "description": "Test the implementation and fix any issues",
                    "effort": "2 hours",
                    "dependencies": ["Implementation"],
                    "assignee_role": "QA Engineer"
                },
                {
                    "title": "Documentation",
                    "description": "Document the implementation and usage",
                    "effort": "1 hour",
                    "dependencies": ["Implementation"],
                    "assignee_role": "Technical Writer"
                }
            ]
            
            # Format the subtasks as a readable response
            response = f"I've decomposed the task '{task_description}' into the following subtasks:\n\n"
            
            for i, subtask in enumerate(subtasks, 1):
                response += f"**Subtask {i}: {subtask['title']}**\n"
                response += f"Description: {subtask['description']}\n"
                response += f"Effort: {subtask['effort']}\n"
                
                if subtask['dependencies']:
                    response += f"Dependencies: {', '.join(subtask['dependencies'])}\n"
                else:
                    response += "Dependencies: None\n"
                    
                response += f"Assignee Role: {subtask['assignee_role']}\n\n"
            
            return response
    
    def create_github_issue(self, repository, title, description):
        """Create a GitHub issue for a task"""
        # This would connect to the GitHub API
        # For now, return a sample response
        return {
            "success": True,
            "issue_number": 42,
            "url": f"https://github.com/{repository}/issues/42"
        }
    
    def create_youtrack_issue(self, project, title, description):
        """Create a YouTrack issue for a task"""
        # This would connect to the YouTrack API
        # For now, return a sample response
        return {
            "success": True,
            "issue_id": "PROJ-123",
            "url": f"https://youtrack.example.com/issue/PROJ-123"
        }
