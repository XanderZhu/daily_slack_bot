import logging
import schedule
import time
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def setup_scheduler(app, agent_network):
    """Set up scheduled tasks for the Slack bot"""
    logger.info("Setting up scheduler for daily and hourly tasks")
    
    # Schedule the daily welcome message (9 AM on weekdays)
    schedule.every().monday.at("09:00").do(send_welcome_message, app=app, agent_network=agent_network)
    schedule.every().tuesday.at("09:00").do(send_welcome_message, app=app, agent_network=agent_network)
    schedule.every().wednesday.at("09:00").do(send_welcome_message, app=app, agent_network=agent_network)
    schedule.every().thursday.at("09:00").do(send_welcome_message, app=app, agent_network=agent_network)
    schedule.every().friday.at("09:00").do(send_welcome_message, app=app, agent_network=agent_network)
    
    # Schedule hourly check-ins (on the hour, during work hours on weekdays)
    for hour in range(10, 18):  # 10 AM to 5 PM
        schedule.every().monday.at(f"{hour:02d}:00").do(send_hourly_checkin, app=app, agent_network=agent_network)
        schedule.every().tuesday.at(f"{hour:02d}:00").do(send_hourly_checkin, app=app, agent_network=agent_network)
        schedule.every().wednesday.at(f"{hour:02d}:00").do(send_hourly_checkin, app=app, agent_network=agent_network)
        schedule.every().thursday.at(f"{hour:02d}:00").do(send_hourly_checkin, app=app, agent_network=agent_network)
        schedule.every().friday.at(f"{hour:02d}:00").do(send_hourly_checkin, app=app, agent_network=agent_network)
    
    # Schedule activity checks (every 2 hours during work hours on weekdays)
    for hour in range(11, 18, 2):  # 11 AM, 1 PM, 3 PM, 5 PM
        schedule.every().monday.at(f"{hour:02d}:00").do(check_activity, app=app, agent_network=agent_network)
        schedule.every().tuesday.at(f"{hour:02d}:00").do(check_activity, app=app, agent_network=agent_network)
        schedule.every().wednesday.at(f"{hour:02d}:00").do(check_activity, app=app, agent_network=agent_network)
        schedule.every().thursday.at(f"{hour:02d}:00").do(check_activity, app=app, agent_network=agent_network)
        schedule.every().friday.at(f"{hour:02d}:00").do(check_activity, app=app, agent_network=agent_network)
    
    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    logger.info("Scheduler set up successfully")

def run_scheduler():
    """Run the scheduler in a loop"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def send_welcome_message(app, agent_network):
    """Send the daily welcome message to all users"""
    logger.info("Sending daily welcome message")
    
    try:
        # Get all users who should receive the welcome message
        users = get_active_users(app)
        
        for user_id in users:
            # Generate the welcome message
            welcome_message = agent_network.send_welcome_message(user_id)
            
            # Send the message
            app.client.chat_postMessage(
                channel=user_id,
                text=welcome_message
            )
            
            logger.info(f"Sent welcome message to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")

def send_hourly_checkin(app, agent_network):
    """Send hourly check-in messages to all users"""
    logger.info("Sending hourly check-in messages")
    
    try:
        # Get all users who should receive the check-in
        users = get_active_users(app)
        
        for user_id in users:
            # Generate the check-in message
            checkin_message = agent_network.send_hourly_checkin(user_id)
            
            # Send the message
            app.client.chat_postMessage(
                channel=user_id,
                text=checkin_message
            )
            
            logger.info(f"Sent hourly check-in to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending hourly check-in: {e}")

def check_activity(app, agent_network):
    """Check user activity and send support messages if needed"""
    logger.info("Checking user activity")
    
    try:
        # Get all users to check activity for
        users = get_active_users(app)
        
        for user_id in users:
            # Check user activity
            activity_message = agent_network.check_activity(user_id)
            
            # If activity has decreased, send a support message
            if activity_message:
                app.client.chat_postMessage(
                    channel=user_id,
                    text=activity_message
                )
                
                logger.info(f"Sent activity support message to user {user_id}")
    except Exception as e:
        logger.error(f"Error checking activity: {e}")

def get_active_users(app):
    """Get a list of active users who should receive messages"""
    try:
        # Get all users in the workspace
        response = app.client.users_list()
        
        # Filter for real, active users (not bots, not deleted, not restricted)
        active_users = []
        for user in response["members"]:
            if (not user.get("is_bot", False) and 
                not user.get("deleted", False) and 
                not user.get("is_restricted", False) and
                not user.get("is_ultra_restricted", False)):
                active_users.append(user["id"])
        
        return active_users
    except Exception as e:
        logger.error(f"Error getting active users: {e}")
        return []
