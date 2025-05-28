import logging
import autogen
import random
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MotivatorAgent:
    """
    The Motivator Agent provides psychological support and motivation.
    It helps users stay motivated, overcome challenges, and maintain wellbeing.
    """
    
    def __init__(self, config_list):
        """Initialize the Motivator Agent"""
        self.config_list = config_list
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="Motivator",
            llm_config={"config_list": config_list},
            system_message="""You are the Motivator Agent responsible for providing psychological support and motivation.
            Your role is to help users stay motivated, overcome challenges, and maintain their wellbeing.
            You should provide encouragement, recognize achievements, offer strategies for overcoming obstacles,
            and help users maintain a positive mindset. Your tone should be supportive, empathetic, and uplifting."""
        )
    
    def process_request(self, user_id, text):
        """Process a motivation or support request"""
        logger.info(f"Motivator processing request from user {user_id}")
        
        # Use AutoGen to generate a response
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER"
        )
        
        # Create a message for motivation
        motivation_prompt = f"""
        User request: {text}
        
        Analyze this request and provide motivational support. Consider:
        1. Acknowledging any challenges or frustrations
        2. Offering encouragement and positive reinforcement
        3. Suggesting practical strategies for overcoming obstacles
        4. Helping maintain perspective and a growth mindset
        
        Respond with supportive, empathetic, and motivational advice.
        """
        
        # Get the motivation response
        user_proxy.initiate_chat(
            self.agent,
            message=motivation_prompt
        )
        
        # Extract the last message from the agent
        chat_history = user_proxy.chat_history[self.agent]
        if chat_history:
            return chat_history[-1]["content"]
        else:
            return "I'm here to support you. What challenges are you facing that I can help with?"
    
    def generate_motivation(self, user_id):
        """Generate a motivational message based on user context"""
        # In a real implementation, this would consider user preferences and history
        motivational_messages = [
            "Remember that progress isn't always linear. Small steps forward still count as progress!",
            "Taking short breaks can actually boost your productivity. Consider the Pomodoro technique.",
            "You've overcome challenges before, and you can do it again. I believe in your abilities!",
            "Focus on what you can control, and try not to worry about what you can't.",
            "It's okay to ask for help when you need it. That's a sign of strength, not weakness.",
            "Remember your 'why' - the purpose behind what you're working on.",
            "Celebrate your small wins along the way. They add up to big accomplishments!",
            "Your worth isn't measured by your productivity. It's okay to have off days.",
            "Try breaking down your task into smaller, more manageable pieces.",
            "Sometimes a change of environment can help refresh your perspective."
        ]
        
        return random.choice(motivational_messages)
    
    def recognize_achievement(self, achievement):
        """Generate a message recognizing a user achievement"""
        recognition_templates = [
            "Great job on {achievement}! Your hard work is paying off.",
            "Congratulations on {achievement}! That's a significant accomplishment.",
            "Awesome work on {achievement}! You should be proud of yourself.",
            "You did it! {achievement} is complete, and that's worth celebrating.",
            "Excellent work completing {achievement}! Your dedication is impressive."
        ]
        
        template = random.choice(recognition_templates)
        return template.format(achievement=achievement)
    
    def suggest_wellbeing_activity(self):
        """Suggest a wellbeing activity for the user"""
        wellbeing_activities = [
            {
                "activity": "Take a 5-minute mindfulness break",
                "description": "Find a quiet spot, close your eyes, and focus on your breathing for 5 minutes."
            },
            {
                "activity": "Stretch break",
                "description": "Stand up and do some gentle stretches to release tension in your neck, shoulders, and back."
            },
            {
                "activity": "Hydration check",
                "description": "Take a moment to drink a glass of water and ensure you're staying hydrated."
            },
            {
                "activity": "Quick walk",
                "description": "Step outside for a 5-10 minute walk to get some fresh air and movement."
            },
            {
                "activity": "Gratitude moment",
                "description": "Take a minute to write down or think about three things you're grateful for today."
            },
            {
                "activity": "Digital detox",
                "description": "Take a 15-minute break from all screens to rest your eyes and mind."
            },
            {
                "activity": "Deep breathing",
                "description": "Practice 4-7-8 breathing: inhale for 4 seconds, hold for 7, exhale for 8."
            },
            {
                "activity": "Desk organization",
                "description": "Take a few minutes to tidy your workspace, which can help clear your mind."
            }
        ]
        
        activity = random.choice(wellbeing_activities)
        return f"**Wellbeing Suggestion:** {activity['activity']}\n{activity['description']}"
    
    def provide_stress_management_tip(self):
        """Provide a tip for managing stress"""
        stress_tips = [
            "Practice progressive muscle relaxation: tense and then release each muscle group in your body.",
            "Try the 5-4-3-2-1 grounding technique: identify 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
            "Write down what's stressing you out, then list what aspects you can control and what you can't.",
            "Take a few minutes to listen to calming music or nature sounds.",
            "Try a quick visualization: imagine yourself in a peaceful place for a few minutes.",
            "Practice saying 'no' to additional commitments when your plate is already full.",
            "Break down overwhelming tasks into smaller, more manageable steps.",
            "Limit caffeine intake, especially later in the day, as it can increase anxiety.",
            "Set boundaries around checking email and messages to reduce constant interruptions.",
            "Remember that it's okay to ask for help or delegate tasks when possible."
        ]
        
        return f"**Stress Management Tip:** {random.choice(stress_tips)}"
