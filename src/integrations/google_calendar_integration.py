import os
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarIntegration:
    """
    Handles integration with the Google Calendar API.
    Provides methods for retrieving, creating, and managing calendar events.
    """
    
    def __init__(self):
        """Initialize the Google Calendar integration"""
        self.credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE")
        self.service = self._get_calendar_service()
    
    def _get_calendar_service(self):
        """Get an authorized Google Calendar API service instance"""
        creds = None
        
        # Check if token.json exists
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_info(token_path, SCOPES)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Build the service
        try:
            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            logger.error(f"Error building Google Calendar service: {e}")
            return None
    
    def get_todays_events(self, calendar_id='primary'):
        """Get events for today from the calendar"""
        if not self.service:
            logger.error("Calendar service not initialized")
            return []
        
        try:
            # Get the start and end of today
            now = datetime.utcnow()
            start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + 'Z'
            end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format the events
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Convert to datetime object
                if 'T' in start:  # This is a dateTime, not just a date
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    start_time = start_dt.strftime('%H:%M')
                else:
                    start_time = 'All day'
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'time': start_time,
                    'duration': self._calculate_duration(event),
                    'location': event.get('location', 'Not specified'),
                    'attendees': self._format_attendees(event.get('attendees', []))
                })
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting today's events: {e}")
            return []
    
    def get_upcoming_events(self, calendar_id='primary', days=7, max_results=10):
        """Get upcoming events for the next few days"""
        if not self.service:
            logger.error("Calendar service not initialized")
            return []
        
        try:
            # Get the current time and the end time
            now = datetime.utcnow().isoformat() + 'Z'
            end_time = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format the events
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Convert to datetime object
                if 'T' in start:  # This is a dateTime, not just a date
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    start_date = start_dt.strftime('%Y-%m-%d')
                    start_time = start_dt.strftime('%H:%M')
                else:
                    start_date = start
                    start_time = 'All day'
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'date': start_date,
                    'time': start_time,
                    'duration': self._calculate_duration(event),
                    'location': event.get('location', 'Not specified'),
                    'attendees': self._format_attendees(event.get('attendees', []))
                })
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting upcoming events: {e}")
            return []
    
    def create_event(self, summary, start_time, end_time, description=None, location=None, attendees=None, calendar_id='primary'):
        """Create a new calendar event"""
        if not self.service:
            logger.error("Calendar service not initialized")
            return None
        
        try:
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                }
            }
            
            # Add attendees if provided
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Call the Calendar API to create the event
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'  # Send updates to all attendees
            ).execute()
            
            return {
                'success': True,
                'event_id': event['id'],
                'html_link': event['htmlLink']
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def find_free_time(self, attendees, duration_minutes=60, days_ahead=7, calendar_id='primary'):
        """Find free time slots for a meeting with multiple attendees"""
        if not self.service:
            logger.error("Calendar service not initialized")
            return []
        
        try:
            # Calculate time range
            now = datetime.utcnow()
            start_time = now.isoformat() + 'Z'
            end_time = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Set up the FreeBusy request
            free_busy_request = {
                'timeMin': start_time,
                'timeMax': end_time,
                'items': [{'id': calendar_id}]  # Start with the primary calendar
            }
            
            # Add attendees' calendars if available
            for attendee in attendees:
                free_busy_request['items'].append({'id': attendee})
            
            # Call the FreeBusy API
            free_busy_response = self.service.freebusy().query(body=free_busy_request).execute()
            
            # Process the response to find free time slots
            # This is a simplified implementation
            # In a real implementation, you would need to analyze the busy times
            # and find gaps that are at least as long as the requested duration
            
            # For now, return some sample time slots
            free_slots = []
            
            # Generate sample time slots for the next few days
            for day in range(days_ahead):
                day_date = now + timedelta(days=day)
                
                # Only consider weekdays
                if day_date.weekday() < 5:  # Monday to Friday
                    # Morning slot
                    morning_start = datetime(day_date.year, day_date.month, day_date.day, 10, 0)
                    morning_end = morning_start + timedelta(minutes=duration_minutes)
                    
                    free_slots.append({
                        'date': morning_start.strftime('%Y-%m-%d'),
                        'start_time': morning_start.strftime('%H:%M'),
                        'end_time': morning_end.strftime('%H:%M')
                    })
                    
                    # Afternoon slot
                    afternoon_start = datetime(day_date.year, day_date.month, day_date.day, 14, 0)
                    afternoon_end = afternoon_start + timedelta(minutes=duration_minutes)
                    
                    free_slots.append({
                        'date': afternoon_start.strftime('%Y-%m-%d'),
                        'start_time': afternoon_start.strftime('%H:%M'),
                        'end_time': afternoon_end.strftime('%H:%M')
                    })
            
            return free_slots
            
        except Exception as e:
            logger.error(f"Error finding free time: {e}")
            return []
    
    def _calculate_duration(self, event):
        """Calculate the duration of an event in minutes"""
        try:
            start = event['start'].get('dateTime')
            end = event['end'].get('dateTime')
            
            if start and end:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                
                duration = (end_dt - start_dt).total_seconds() / 60
                return int(duration)
            
            return 0  # For all-day events or events without clear times
            
        except Exception as e:
            logger.warning(f"Error calculating event duration: {e}")
            return 60  # Default to 60 minutes
    
    def _format_attendees(self, attendees):
        """Format the attendees list"""
        return [attendee.get('email') for attendee in attendees]
