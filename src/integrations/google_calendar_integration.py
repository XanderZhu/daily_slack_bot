import os
import logging
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GoogleCalendarIntegration:
    """
    Handles integration with the Google Calendar API (mocked version).
    Provides methods for retrieving, creating, and managing calendar events.
    """
    
    def __init__(self):
        """Initialize the Google Calendar integration with mock data"""
        self.user_manager = None  # Will be set by the initializer
        logger.info("Initializing Google Calendar integration with mock data")
        
        # Create mock data
        self.mock_events = self._generate_mock_events()
    
    def _generate_mock_events(self):
        """Generate mock calendar events"""
        # Get current date and time
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Common meeting titles
        meeting_titles = [
            "Team Standup", 
            "Project Planning", 
            "Code Review", 
            "1:1 with Manager", 
            "Sprint Planning", 
            "Retrospective", 
            "Product Demo", 
            "Client Meeting", 
            "Technical Discussion", 
            "Lunch Break"
        ]
        
        # Common locations
        locations = [
            "Conference Room A", 
            "Conference Room B", 
            "Zoom Meeting", 
            "Google Meet", 
            "Office Kitchen", 
            "Main Office", 
            "Client Office", 
            "Virtual"
        ]
        
        # Generate events for the next 14 days
        events = []
        for day in range(14):
            # Skip weekends (5=Saturday, 6=Sunday)
            current_date = today + timedelta(days=day)
            if current_date.weekday() >= 5:
                continue
                
            # Generate 3-6 events per day
            num_events = random.randint(3, 6)
            for i in range(num_events):
                # Random start time between 9 AM and 5 PM
                start_hour = random.randint(9, 16)  # Up to 4 PM to allow for 1-hour meetings
                start_minute = random.choice([0, 15, 30, 45])
                
                # Random duration between 30 and 90 minutes
                duration = random.choice([30, 45, 60, 90])
                
                # Calculate start and end times
                start_time = current_date.replace(hour=start_hour, minute=start_minute)
                end_time = start_time + timedelta(minutes=duration)
                
                # Create event
                event_id = f"event_{day}_{i}"
                event = {
                    "id": event_id,
                    "summary": random.choice(meeting_titles),
                    "location": random.choice(locations),
                    "description": f"Mock calendar event {event_id}",
                    "start": {
                        "dateTime": start_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": end_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "attendees": [
                        {"email": f"attendee{j}@example.com"} for j in range(random.randint(1, 5))
                    ],
                    "created": (now - timedelta(days=random.randint(1, 30))).isoformat()
                }
                
                events.append(event)
        
        return events
    
    def get_todays_events(self, calendar_id='primary'):
        """Get events for today from the calendar (mocked)"""
        try:
            # Get current date
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            # Filter events for today
            todays_events = []
            for event in self.mock_events:
                start_time_str = event['start'].get('dateTime')
                if not start_time_str:
                    continue
                    
                # Convert to datetime
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00') if 'Z' in start_time_str else start_time_str)
                
                # Check if event is today
                if today <= start_time < tomorrow:
                    todays_events.append(event)
            
            # Format the events
            formatted_events = []
            for event in todays_events:
                start_time_str = event['start'].get('dateTime')
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00') if 'Z' in start_time_str else start_time_str)
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'time': start_time.strftime('%H:%M'),
                    'duration': self._calculate_duration(event),
                    'location': event.get('location', 'Not specified'),
                    'attendees': self._format_attendees(event.get('attendees', []))
                })
            
            # Sort by start time
            formatted_events.sort(key=lambda x: x['time'])
            
            logger.info(f"Retrieved {len(formatted_events)} mock events for today")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting today's mock events: {e}")
            return []
    
    def get_upcoming_events(self, calendar_id='primary', days=7, max_results=10):
        """Get upcoming events for the next few days (mocked)"""
        try:
            # Get current date and time
            now = datetime.now()
            end_date = now + timedelta(days=days)
            
            # Filter events for the specified period
            upcoming_events = []
            for event in self.mock_events:
                start_time_str = event['start'].get('dateTime')
                if not start_time_str:
                    continue
                    
                # Convert to datetime
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00') if 'Z' in start_time_str else start_time_str)
                
                # Check if event is in the specified period
                if now <= start_time < end_date:
                    upcoming_events.append(event)
            
            # Sort by start time
            upcoming_events.sort(key=lambda x: x['start'].get('dateTime', ''))
            
            # Limit results
            upcoming_events = upcoming_events[:max_results]
            
            # Format the events
            formatted_events = []
            for event in upcoming_events:
                start_time_str = event['start'].get('dateTime')
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00') if 'Z' in start_time_str else start_time_str)
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'date': start_time.strftime('%Y-%m-%d'),
                    'time': start_time.strftime('%H:%M'),
                    'duration': self._calculate_duration(event),
                    'location': event.get('location', 'Not specified'),
                    'attendees': self._format_attendees(event.get('attendees', []))
                })
            
            logger.info(f"Retrieved {len(formatted_events)} mock upcoming events")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting upcoming mock events: {e}")
            return []
    
    def create_event(self, summary, start_time, end_time, description=None, location=None, attendees=None, calendar_id='primary'):
        """Create a new calendar event (mocked)"""
        try:
            # Generate a unique ID for the event
            event_id = f"event_{len(self.mock_events) + 1}"
            
            # Format attendees if provided
            formatted_attendees = None
            if attendees:
                formatted_attendees = [{'email': attendee} for attendee in attendees]
            
            # Create the new event
            new_event = {
                'id': event_id,
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'created': datetime.now().isoformat()
            }
            
            if description:
                new_event['description'] = description
            
            if location:
                new_event['location'] = location
            
            if formatted_attendees:
                new_event['attendees'] = formatted_attendees
            
            # Add to mock events
            self.mock_events.append(new_event)
            
            logger.info(f"Created mock calendar event '{summary}' with ID {event_id}")
            
            return {
                'success': True,
                'event_id': event_id
            }
            
        except Exception as e:
            logger.error(f"Error creating mock calendar event: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def find_free_time(self, attendees, duration_minutes=60, days_ahead=7, calendar_id='primary'):
        """Find free time slots for a meeting with multiple attendees (mocked)"""
        try:
            # Get current date and time
            now = datetime.now()
            end_date = now + timedelta(days=days_ahead)
            
            # Get busy times from mock events
            busy_times = []
            for event in self.mock_events:
                start_time_str = event['start'].get('dateTime')
                end_time_str = event['end'].get('dateTime')
                
                if not start_time_str or not end_time_str:
                    continue
                    
                # Convert to datetime
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00') if 'Z' in start_time_str else start_time_str)
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00') if 'Z' in end_time_str else end_time_str)
                
                # Check if event is in the specified period
                if (start_time < end_date and end_time > now):
                    busy_times.append((start_time, end_time))
            
            # Sort busy times by start time
            busy_times.sort(key=lambda x: x[0])
            
            # Find free slots
            free_slots = []
            current_date = now.replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM
            
            # Loop through each day
            while current_date < end_date:
                # Skip weekends
                if current_date.weekday() >= 5:  # Saturday or Sunday
                    current_date = current_date + timedelta(days=1)  # Move to next day
                    current_date = current_date.replace(hour=9, minute=0, second=0, microsecond=0)  # Reset to 9 AM
                    continue
                
                # Define work hours: 9 AM to 5 PM
                day_start = current_date
                day_end = current_date.replace(hour=17, minute=0, second=0, microsecond=0)  # 5 PM
                
                # Find free slots for this day
                time_slots = self._find_free_slots_for_day(day_start, day_end, busy_times, duration_minutes)
                free_slots.extend(time_slots)
                
                # Move to next day
                current_date = current_date + timedelta(days=1)
                current_date = current_date.replace(hour=9, minute=0, second=0, microsecond=0)  # Reset to 9 AM
            
            logger.info(f"Found {len(free_slots)} mock free time slots")
            return free_slots
            
        except Exception as e:
            logger.error(f"Error finding mock free time: {e}")
            return []
    
    def _find_free_slots_for_day(self, day_start, day_end, busy_times, duration_minutes):
        """Helper method to find free slots for a specific day"""
        free_slots = []
        current_time = day_start
        duration_delta = timedelta(minutes=duration_minutes)
        
        # Filter busy times for this day
        day_busy_times = []
        for start, end in busy_times:
            # Check if the busy time overlaps with this day
            if start.date() == day_start.date() or end.date() == day_start.date():
                # Clip to day boundaries
                clipped_start = max(start, day_start)
                clipped_end = min(end, day_end)
                if clipped_start < clipped_end:  # Only add if there's an actual overlap
                    day_busy_times.append((clipped_start, clipped_end))
        
        # Sort by start time
        day_busy_times.sort(key=lambda x: x[0])
        
        # Find free slots
        for busy_start, busy_end in day_busy_times:
            # Check if there's a free slot before this busy time
            if busy_start - current_time >= duration_delta:
                # Add free slot
                slot_end = current_time + duration_delta
                free_slots.append({
                    'date': current_time.strftime('%Y-%m-%d'),
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M')
                })
            
            # Move current time to after this busy period
            current_time = busy_end
        
        # Check for a final free slot after the last busy time
        if day_end - current_time >= duration_delta:
            slot_end = current_time + duration_delta
            free_slots.append({
                'date': current_time.strftime('%Y-%m-%d'),
                'start_time': current_time.strftime('%H:%M'),
                'end_time': slot_end.strftime('%H:%M')
            })
        
        return free_slots
    
    def _calculate_duration(self, event):
        """Calculate the duration of an event in minutes"""
        try:
            start_time_str = event['start'].get('dateTime')
            end_time_str = event['end'].get('dateTime')
            
            if start_time_str and end_time_str:
                # Convert to datetime objects
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00') if 'Z' in start_time_str else start_time_str)
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00') if 'Z' in end_time_str else end_time_str)
                
                # Calculate duration in minutes
                duration = (end_time - start_time).total_seconds() / 60
                return int(duration)
            
            return 0  # For all-day events or events without clear times
            
        except Exception as e:
            logger.warning(f"Error calculating mock event duration: {e}")
            return 60  # Default to 60 minutes
    
    def _format_attendees(self, attendees):
        """Format the attendees list"""
        if not attendees:
            return []
        return [attendee.get('email') for attendee in attendees if attendee.get('email')]
