# Daily Slack Bot

A Slack bot that provides daily support and assistance to employees through an AutoGen agent network.

## Features

- Daily welcome message with meeting and task summaries
- Hourly check-ins to offer assistance
- Activity monitoring (GitHub, Slack)
- Support services:
  - Research assistance
  - Psychological support
  - Planning help
  - Communication assistance
  - Task decomposition
  - Code assistance

## Agent Network

The bot utilizes an AutoGen network with specialized agents:
1. Head Manager - Coordinates all other agents
2. Daily Planner - Helps plan the day's activities
3. Project Analyst - Decomposes complex tasks
4. Motivator - Provides psychological support
5. Developer Assistant - Helps with coding tasks
6. Research Agent - Assists with information gathering
7. Communication Agent - Helps with meetings and messages

## Integrations

- Slack
- GitHub
- Gmail
- Google Calendar
- YouTrack

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:
   ```
   SLACK_BOT_TOKEN=your_slack_bot_token
   SLACK_SIGNING_SECRET=your_slack_signing_secret
   SLACK_APP_TOKEN=your_slack_app_token
   
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

3. Run the bot:
   ```
   python app.py
   ```

## User Onboarding

When a user first interacts with the bot, they will go through an onboarding process to set up their integrations:

1. **Welcome Message**: The bot introduces itself and explains the onboarding process

2. **GitHub Integration**: The user is prompted to provide their GitHub personal access token

3. **Google Integration**: The user is guided through setting up Google Calendar and Gmail access

4. **YouTrack Integration**: The user is prompted to provide their YouTrack URL and token

Users can skip any integration they don't want to set up immediately and complete it later.

## Data Storage and Credential Management

All user data, preferences, and credentials are securely stored in Supabase:

- **Users Table**: Stores user profiles, preferences, and onboarding status
- **Credentials Table**: Securely stores API tokens and credentials for:
  - GitHub
  - YouTrack
  - Google (Calendar and Gmail)
- **Interactions Table**: Logs user interactions with the bot

This provides a more secure and scalable solution compared to local file storage, allowing the bot to be deployed across multiple instances while maintaining consistent user data.
