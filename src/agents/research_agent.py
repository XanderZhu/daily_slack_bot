import logging
import autogen
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    The Research Agent helps gather and analyze information.
    It provides research assistance, information synthesis, and knowledge retrieval.
    """
    
    def __init__(self, config_list):
        """Initialize the Research Agent"""
        self.config_list = config_list
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="ResearchAgent",
            llm_config={"config_list": config_list},
            system_message="""You are the Research Agent responsible for gathering and analyzing information.
            Your role is to help users find relevant information, synthesize data from multiple sources,
            and provide well-researched answers to questions. You should be thorough, accurate, and
            able to present complex information in a clear, accessible way."""
        )
    
    def process_request(self, user_id, text):
        """Process a research-related request"""
        logger.info(f"Research Agent processing request from user {user_id}")
        
        # Use AutoGen to generate a response
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for research
        research_prompt = f"""
        User request: {text}
        
        Analyze this request and provide research assistance. Consider:
        1. Understanding the core information need
        2. Identifying key concepts and search terms
        3. Suggesting reliable sources of information
        4. Synthesizing information from multiple sources
        5. Presenting findings in a clear, structured format
        
        Respond with helpful, well-researched information.
        """
        
        # Get the research response
        user_proxy.initiate_chat(
            self.agent,
            message=research_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            return "I can help you research that topic. What specific information are you looking for?"
    
    def search_information(self, query, max_results=5):
        """Search for information on a given query"""
        # This would connect to search APIs or knowledge bases
        # For now, return a placeholder response
        return f"Here are some search results for '{query}'. In a real implementation, this would connect to search APIs or knowledge bases to provide actual results."
    
    def summarize_article(self, article_text):
        """Summarize an article or document"""
        # Use AutoGen to generate a summary
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for summarization
        summary_prompt = f"""
        Article text:
        {article_text[:1000]}... [truncated for brevity]
        
        Please provide a concise summary of this article. Include:
        1. The main topic and purpose
        2. Key points and findings
        3. Any important conclusions or implications
        
        Format the response as a brief, informative summary.
        """
        
        # Get the summary response
        user_proxy.initiate_chat(
            self.agent,
            message=summary_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback summary if AutoGen fails
            return "I'd be happy to summarize this article for you. Let me analyze the content and extract the key points."
    
    def find_resources(self, topic, resource_type="article"):
        """Find resources on a specific topic"""
        # This would connect to APIs or databases to find resources
        # For now, return sample data
        resources = [
            {
                "title": f"Introduction to {topic}",
                "type": resource_type,
                "url": f"https://example.com/{topic.lower().replace(' ', '-')}-intro",
                "description": f"A beginner-friendly introduction to {topic}."
            },
            {
                "title": f"Advanced {topic} Techniques",
                "type": resource_type,
                "url": f"https://example.com/{topic.lower().replace(' ', '-')}-advanced",
                "description": f"In-depth coverage of advanced {topic} concepts and techniques."
            },
            {
                "title": f"{topic} Best Practices",
                "type": resource_type,
                "url": f"https://example.com/{topic.lower().replace(' ', '-')}-best-practices",
                "description": f"Industry best practices for {topic}."
            }
        ]
        
        # Format the resources as a readable response
        response = f"Here are some resources on {topic}:\n\n"
        
        for resource in resources:
            response += f"**{resource['title']}**\n"
            response += f"Type: {resource['type']}\n"
            response += f"URL: {resource['url']}\n"
            response += f"Description: {resource['description']}\n\n"
        
        return response
    
    def compare_options(self, options, criteria):
        """Compare multiple options based on specified criteria"""
        # Use AutoGen to generate a comparison
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for comparison
        comparison_prompt = f"""
        Options to compare:
        {', '.join(options)}
        
        Criteria for comparison:
        {', '.join(criteria)}
        
        Please compare these options based on the specified criteria. Include:
        1. A brief overview of each option
        2. An analysis of how each option performs against each criterion
        3. A summary of strengths and weaknesses
        4. A recommendation based on the comparison
        
        Format the response as a structured comparison.
        """
        
        # Get the comparison response
        user_proxy.initiate_chat(
            self.agent,
            message=comparison_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            # Fallback comparison if AutoGen fails
            return f"I'd be happy to compare {', '.join(options)} based on {', '.join(criteria)}. Let me analyze each option against these criteria."
