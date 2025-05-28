"""
Mock classes for integration testing
"""

class MockSlackIntegration:
    """Mock implementation of SlackIntegration for testing"""
    
    def __init__(self):
        self.messages = []
        self.users = {
            "test_user": {
                "id": "test_user",
                "name": "Test User",
                "real_name": "Test User",
                "profile": {
                    "email": "test@example.com"
                }
            }
        }
    
    def send_message(self, user_id, text, blocks=None):
        """Mock sending a message to a user"""
        self.messages.append({
            "user_id": user_id,
            "text": text,
            "blocks": blocks
        })
        return True
    
    def get_user_info(self, user_id):
        """Mock getting user info"""
        return self.users.get(user_id)
    
    def get_bot_id(self):
        """Mock getting bot ID"""
        return "test_bot"


class MockGitHubIntegration:
    """Mock implementation of GitHubIntegration for testing"""
    
    def __init__(self):
        self.issues = [
            {
                "id": "issue1",
                "title": "Fix bug in login flow",
                "body": "Users are experiencing issues with the login flow",
                "state": "open",
                "priority": "high",
                "url": "https://github.com/org/repo/issues/1"
            },
            {
                "id": "issue2",
                "title": "Implement new feature",
                "body": "Add new dashboard feature",
                "state": "open",
                "priority": "medium",
                "url": "https://github.com/org/repo/issues/2"
            }
        ]
    
    def get_user_issues(self, username):
        """Mock getting user issues"""
        return self.issues
    
    def get_user_activity(self, username, days=7):
        """Mock getting user activity"""
        return {
            "commits": 10,
            "pull_requests": 2,
            "comments": 5
        }


class MockGoogleCalendarIntegration:
    """Mock implementation of GoogleCalendarIntegration for testing"""
    
    def __init__(self):
        self.events = [
            {
                "id": "event1",
                "title": "Team Meeting",
                "time": "10:00",
                "duration": "1 hour",
                "attendees": ["test@example.com", "colleague@example.com"],
                "location": "Conference Room A"
            },
            {
                "id": "event2",
                "title": "Project Review",
                "time": "14:00",
                "duration": "30 minutes",
                "attendees": ["test@example.com", "manager@example.com"],
                "location": "Zoom"
            }
        ]
    
    def get_today_events(self, user_id):
        """Mock getting today's events"""
        return self.events
    
    def create_event(self, user_id, title, start_time, end_time, attendees=None, location=None):
        """Mock creating an event"""
        new_event = {
            "id": f"event{len(self.events) + 1}",
            "title": title,
            "time": start_time,
            "duration": "1 hour",  # Simplified
            "attendees": attendees or [],
            "location": location or "Not specified"
        }
        self.events.append(new_event)
        return new_event


class MockGmailIntegration:
    """Mock implementation of GmailIntegration for testing"""
    
    def __init__(self):
        self.emails = [
            {
                "id": "email1",
                "subject": "Important Project Update",
                "sender": "manager@example.com",
                "snippet": "Here's the latest update on our project...",
                "date": "2025-05-28T09:30:00Z",
                "read": False
            },
            {
                "id": "email2",
                "subject": "Meeting Notes",
                "sender": "colleague@example.com",
                "snippet": "Attached are the notes from yesterday's meeting...",
                "date": "2025-05-27T16:45:00Z",
                "read": True
            }
        ]
        self.drafts = []
    
    def get_unread_emails(self, user_id):
        """Mock getting unread emails"""
        return [email for email in self.emails if not email["read"]]
    
    def create_draft(self, user_id, to, subject, body):
        """Mock creating a draft email"""
        draft = {
            "id": f"draft{len(self.drafts) + 1}",
            "to": to,
            "subject": subject,
            "body": body
        }
        self.drafts.append(draft)
        return draft


class MockYouTrackIntegration:
    """Mock implementation of YouTrackIntegration for testing"""
    
    def __init__(self):
        self.tasks = [
            {
                "id": "task1",
                "title": "Implement user authentication",
                "description": "Add user authentication to the application",
                "state": "Open",
                "priority": "Critical",
                "url": "https://youtrack.example.com/issue/task1"
            },
            {
                "id": "task2",
                "title": "Write documentation",
                "description": "Create user documentation for the new features",
                "state": "Open",
                "priority": "Normal",
                "url": "https://youtrack.example.com/issue/task2"
            }
        ]
    
    def get_user_tasks(self, user_id):
        """Mock getting user tasks"""
        return self.tasks
    
    def create_task(self, user_id, title, description, priority="Normal"):
        """Mock creating a task"""
        task = {
            "id": f"task{len(self.tasks) + 1}",
            "title": title,
            "description": description,
            "state": "Open",
            "priority": priority,
            "url": f"https://youtrack.example.com/issue/task{len(self.tasks) + 1}"
        }
        self.tasks.append(task)
        return task


class MockSupabaseIntegration:
    """Mock implementation of SupabaseIntegration for testing"""
    
    def __init__(self):
        self.users = {
            "test_user": {
                "id": "test_user",
                "email": "test@example.com",
                "name": "Test User",
                "settings": {
                    "notifications_enabled": True,
                    "daily_summary_time": "09:00"
                },
                "onboarding_completed": True
            }
        }
        self.interactions = []
    
    def get_user(self, user_id):
        """Mock getting user data"""
        return self.users.get(user_id)
    
    def update_user(self, user_id, data):
        """Mock updating user data"""
        if user_id in self.users:
            self.users[user_id].update(data)
            return self.users[user_id]
        return None
    
    def log_interaction(self, user_id, interaction_type, data=None):
        """Mock logging an interaction"""
        interaction = {
            "id": len(self.interactions) + 1,
            "user_id": user_id,
            "type": interaction_type,
            "data": data or {},
            "timestamp": "2025-05-28T18:30:00Z"  # Simplified
        }
        self.interactions.append(interaction)
        return interaction
