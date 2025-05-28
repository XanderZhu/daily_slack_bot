import logging
import autogen
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DeveloperAssistantAgent:
    """
    The Developer Assistant Agent helps with coding tasks and technical challenges.
    It provides code suggestions, debugging help, and technical guidance.
    """
    
    def __init__(self, config_list):
        """Initialize the Developer Assistant Agent"""
        self.config_list = config_list
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="DeveloperAssistant",
            llm_config={"config_list": config_list},
            system_message="""You are the Developer Assistant Agent responsible for helping with coding tasks.
            Your role is to provide code suggestions, debugging help, and technical guidance.
            You should help users solve programming problems, understand error messages,
            and implement best practices in their code. Your responses should be clear,
            accurate, and focused on practical solutions."""
        )
    
    def process_request(self, user_id, text):
        """Process a coding-related request"""
        logger.info(f"Developer Assistant processing request from user {user_id}")
        
        # Use AutoGen to generate a response
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for coding assistance
        coding_prompt = f"""
        User request: {text}
        
        Analyze this request and provide coding assistance. Consider:
        1. Understanding the technical problem or requirement
        2. Suggesting appropriate solutions or approaches
        3. Providing clear, well-commented code examples if needed
        4. Explaining the reasoning behind your suggestions
        5. Highlighting best practices and potential pitfalls
        
        Respond with helpful, practical coding advice.
        """
        
        # Get the coding assistance response
        user_proxy.initiate_chat(
            self.agent,
            message=coding_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            return "I can help with your coding tasks. What specific technical challenge are you facing?"
    
    def get_github_activity(self, user_id):
        """Get GitHub activity for a user"""
        # This would connect to the GitHub API
        # For now, return sample data
        return {
            "commits_today": 2,
            "commits_yesterday": 5,
            "pull_requests_open": 1,
            "issues_assigned": 3,
            "decreased": True  # For demonstration purposes
        }
    
    def suggest_code_solution(self, problem_description, language):
        """Suggest a code solution for a given problem"""
        # Use AutoGen to generate a code solution
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for code solution
        solution_prompt = f"""
        Problem description: {problem_description}
        Programming language: {language}
        
        Please provide a code solution for this problem. Include:
        1. A clear explanation of your approach
        2. Well-commented, readable code
        3. Any relevant best practices or optimizations
        4. Potential edge cases to consider
        
        Format the response with a brief explanation followed by the code solution.
        """
        
        # Get the solution response
        user_proxy.initiate_chat(
            self.agent,
            message=solution_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback solution if AutoGen fails
            return f"I'd be happy to help with your {language} coding problem. Could you provide more details about what you're trying to accomplish?"
    
    def debug_code(self, code, error_message, language):
        """Help debug code based on an error message"""
        # Use AutoGen to generate debugging help
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for debugging
        debug_prompt = f"""
        Code with issue:
        ```{language}
        {code}
        ```
        
        Error message:
        ```
        {error_message}
        ```
        
        Please analyze this code and error message. Provide:
        1. An explanation of what's causing the error
        2. A solution to fix the issue
        3. Any suggestions for improving the code
        
        Format the response with a clear explanation and the corrected code.
        """
        
        # Get the debugging response
        user_proxy.initiate_chat(
            self.agent,
            message=debug_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback debugging if AutoGen fails
            return "I'd be happy to help debug your code. Let me analyze the error message and code to identify the issue."
    
    def suggest_code_improvement(self, code, language):
        """Suggest improvements for existing code"""
        # Use AutoGen to generate improvement suggestions
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for code improvement
        improvement_prompt = f"""
        Existing code:
        ```{language}
        {code}
        ```
        
        Please review this code and suggest improvements. Consider:
        1. Code readability and maintainability
        2. Performance optimizations
        3. Best practices for {language}
        4. Potential bugs or edge cases
        5. Code structure and organization
        
        Format the response with clear explanations for each suggestion.
        """
        
        # Get the improvement response
        user_proxy.initiate_chat(
            self.agent,
            message=improvement_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback improvement if AutoGen fails
            return f"I'd be happy to review your {language} code and suggest improvements. Let me analyze it for readability, performance, and best practices."
