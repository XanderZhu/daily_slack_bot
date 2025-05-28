import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize Slack app
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
handler = SlackRequestHandler(slack_app)

# Initialize Supabase client
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)

@app.post("/slack/events")
async def endpoint(request: Request):
    return await handler.handle(request)

@slack_app.event("message")
def handle_message(event, say):
    try:
        # Extract message data
        user_id = event.get("user")
        text = event.get("text", "")
        channel = event.get("channel")
        ts = event.get("ts")
        
        # Check if user exists in the database
        user_result = supabase.table("users").select("*").eq("slack_id", user_id).execute()
        
        if not user_result.data:
            # Get user info from Slack
            user_info = slack_app.client.users_info(user=user_id)
            user_data = {
                "slack_id": user_id,
                "username": user_info["user"]["name"],
                "real_name": user_info["user"]["real_name"],
                "email": user_info["user"]["profile"].get("email", ""),
                "created_at": datetime.now().isoformat()
            }
            # Insert user into database
            supabase.table("users").insert(user_data).execute()
        
        # Save message to database
        message_data = {
            "user_id": user_id,
            "content": text,
            "channel_id": channel,
            "timestamp": ts,
            "created_at": datetime.now().isoformat()
        }
        supabase.table("messages").insert(message_data).execute()
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 