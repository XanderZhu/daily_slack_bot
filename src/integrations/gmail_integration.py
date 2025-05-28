import os
import logging
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailIntegration:
    """
    Handles integration with the Gmail API.
    Provides methods for sending emails, reading emails, and managing drafts.
    """
    
    def __init__(self):
        """Initialize the Gmail integration"""
        self.credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE")
        self.service = self._get_gmail_service()
    
    def _get_gmail_service(self):
        """Get an authorized Gmail API service instance"""
        creds = None
        
        # Check if token.json exists
        token_path = 'gmail_token.json'
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
            service = build('gmail', 'v1', credentials=creds)
            return service
        except Exception as e:
            logger.error(f"Error building Gmail service: {e}")
            return None
    
    def send_email(self, to, subject, body, cc=None, bcc=None):
        """Send an email"""
        if not self.service:
            logger.error("Gmail service not initialized")
            return None
        
        try:
            # Create the email message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id']
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_draft(self, to, subject, body, cc=None, bcc=None):
        """Create a draft email"""
        if not self.service:
            logger.error("Gmail service not initialized")
            return None
        
        try:
            # Create the email message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create the draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={
                    'message': {
                        'raw': raw_message
                    }
                }
            ).execute()
            
            return {
                'success': True,
                'draft_id': draft['id']
            }
            
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_unread_emails(self, max_results=10):
        """Get unread emails from the inbox"""
        if not self.service:
            logger.error("Gmail service not initialized")
            return []
        
        try:
            # Search for unread emails in the inbox
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get the details of each message
            unread_emails = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                
                # Extract snippet
                snippet = msg.get('snippet', '')
                
                unread_emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': snippet
                })
            
            return unread_emails
            
        except Exception as e:
            logger.error(f"Error getting unread emails: {e}")
            return []
    
    def get_email_content(self, message_id):
        """Get the content of a specific email"""
        if not self.service:
            logger.error("Gmail service not initialized")
            return None
        
        try:
            # Get the message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            to = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown Recipient')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Extract body (simplified, doesn't handle attachments or complex MIME types)
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body']['data']).decode()
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()
            
            return {
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'to': to,
                'date': date,
                'body': body
            }
            
        except Exception as e:
            logger.error(f"Error getting email content: {e}")
            return None
    
    def reply_to_email(self, message_id, body):
        """Reply to an email"""
        if not self.service:
            logger.error("Gmail service not initialized")
            return None
        
        try:
            # Get the original message to extract headers
            original = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['Subject', 'From', 'To', 'Message-ID', 'References', 'In-Reply-To']
            ).execute()
            
            # Extract headers
            headers = original['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            message_id_header = next((h['value'] for h in headers if h['name'] == 'Message-ID'), '')
            references = next((h['value'] for h in headers if h['name'] == 'References'), '')
            
            # Prepare reply headers
            if not subject.startswith('Re:'):
                subject = f"Re: {subject}"
            
            # Create the reply message
            message = MIMEText(body)
            message['to'] = sender
            message['subject'] = subject
            
            # Add threading headers
            if message_id_header:
                if references:
                    message['References'] = f"{references} {message_id_header}"
                else:
                    message['References'] = message_id_header
                message['In-Reply-To'] = message_id_header
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send the reply
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id']
            }
            
        except Exception as e:
            logger.error(f"Error replying to email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
