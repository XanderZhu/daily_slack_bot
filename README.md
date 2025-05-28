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

## Supabase Setup

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new project and note your project URL and API key
3. Set up the following tables in your Supabase database:

### Users Table
```sql
create table public.users (
  id uuid default uuid_generate_v4() primary key,
  slack_id text unique not null,
  name text,
  email text,
  github_username text,
  preferences jsonb default '{}'::jsonb,
  onboarding_started boolean default false,
  onboarding_completed boolean default false,
  onboarding_step text default 'welcome',
  github_setup text,
  google_setup text,
  youtrack_setup text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);
```

### Credentials Table
```sql
create table public.credentials (
  id uuid default uuid_generate_v4() primary key,
  slack_id text references public.users(slack_id),
  credential_type text not null,
  data jsonb not null,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone,
  unique(slack_id, credential_type)
);
```

### Interactions Table
```sql
create table public.interactions (
  id uuid default uuid_generate_v4() primary key,
  slack_id text references public.users(slack_id),
  interaction_type text not null,
  details jsonb,
  created_at timestamp with time zone default now()
);
```
