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
   GITHUB_TOKEN=your_github_token
   GOOGLE_CREDENTIALS_FILE=path_to_credentials.json
   YOUTRACK_TOKEN=your_youtrack_token
   ```

3. Run the bot:
   ```
   python app.py
   ```
