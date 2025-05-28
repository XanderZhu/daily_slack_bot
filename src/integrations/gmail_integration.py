import os
import logging
from datetime import datetime, timedelta
import json
import random
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GmailIntegration:
    """
    Handles integration with the Gmail API (mocked version).
    Provides methods for sending emails, reading emails, and managing drafts.
    """
    
    def __init__(self):
        """Initialize the Gmail integration with mock data"""
        self.user_manager = None  # Will be set by the initializer
        logger.info("Initializing Gmail integration with mock data")
        
        # Create mock data
        self.mock_emails = self._generate_mock_emails()
        self.mock_drafts = self._generate_mock_drafts()
    
    def _generate_mock_emails(self):
        """Generate mock email data"""
        return [
            {
                "id": f"email_{i}",
                "threadId": f"thread_{i//3}",  # Group emails into threads
                "from": f"user{i%5}@example.com",
                "to": "me@example.com",
                "subject": f"Mock Email {i}",
                "body": f"This is the body of mock email {i}",
                "date": (datetime.now() - timedelta(days=i%7, hours=i%24)).isoformat(),
                "read": random.choice([True, False]),
                "labels": random.sample(["INBOX", "IMPORTANT", "CATEGORY_PERSONAL", "CATEGORY_WORK"], k=random.randint(1, 3))
            } for i in range(1, 21)  # Generate 20 mock emails
        ]
    
    def _generate_mock_drafts(self):
        """Generate mock draft data"""
        return [
            {
                "id": f"draft_{i}",
                "to": f"recipient{i}@example.com",
                "subject": f"Draft Email {i}",
                "body": f"This is the body of draft email {i}",
                "date": (datetime.now() - timedelta(days=i%5)).isoformat()
            } for i in range(1, 6)  # Generate 5 mock drafts
        ]
    
    def send_email(self, to, subject, body, cc=None, bcc=None):
        """Send an email (mocked)"""
        try:
            # Create a new mock email
            new_email_id = f"email_{len(self.mock_emails) + 1}"
            thread_id = f"thread_{random.randint(1, 10)}"
            
            new_email = {
                "id": new_email_id,
                "threadId": thread_id,
                "from": "me@example.com",
                "to": to,
                "subject": subject,
                "body": body,
                "date": datetime.now().isoformat(),
                "read": True,
                "labels": ["SENT"]
            }
            
            if cc:
                new_email["cc"] = cc
            if bcc:
                new_email["bcc"] = bcc
                
            # Add to mock emails
            self.mock_emails.append(new_email)
            
            logger.info(f"Mock email sent to {to} with subject '{subject}'")
            
            return {
                'success': True,
                'message_id': new_email_id
            }
            
        except Exception as e:
            logger.error(f"Error sending mock email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_draft(self, to, subject, body, cc=None, bcc=None):
        """Create a draft email (mocked)"""
        try:
            # Create a new mock draft
            new_draft_id = f"draft_{len(self.mock_drafts) + 1}"
            
            new_draft = {
                "id": new_draft_id,
                "to": to,
                "subject": subject,
                "body": body,
                "date": datetime.now().isoformat()
            }
            
            if cc:
                new_draft["cc"] = cc
            if bcc:
                new_draft["bcc"] = bcc
                
            # Add to mock drafts
            self.mock_drafts.append(new_draft)
            
            logger.info(f"Mock draft created to {to} with subject '{subject}'")
            
            return {
                'success': True,
                'draft_id': new_draft_id
            }
            
        except Exception as e:
            logger.error(f"Error creating mock draft: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_unread_emails(self, max_results=10):
        """Get unread emails from the inbox (mocked)"""
        try:
            # Filter unread emails from mock data
            unread_emails = [email for email in self.mock_emails 
                            if not email.get('read') and 'INBOX' in email.get('labels', [])]
            
            # Sort by date (newest first) and limit results
            unread_emails.sort(key=lambda x: x.get('date', ''), reverse=True)
            unread_emails = unread_emails[:max_results]
            
            # Format the response to match the expected structure
            result = []
            for email in unread_emails:
                result.append({
                    'id': email.get('id'),
                    'subject': email.get('subject', 'No Subject'),
                    'sender': email.get('from', 'Unknown Sender'),
                    'date': email.get('date', ''),
                    'snippet': email.get('body', '')[:100] + '...' if len(email.get('body', '')) > 100 else email.get('body', '')
                })
            
            logger.info(f"Retrieved {len(result)} mock unread emails")
            return result
            
        except Exception as e:
            logger.error(f"Error getting mock unread emails: {e}")
            return []
    
    def get_email_content(self, message_id):
        """Get the content of a specific email (mocked)"""
        try:
            # Find the email in our mock data
            email = next((e for e in self.mock_emails if e.get('id') == message_id), None)
            
            if not email:
                logger.error(f"Mock email with ID {message_id} not found")
                return None
            
            # Mark as read
            email['read'] = True
            
            # Format the response
            result = {
                'id': email.get('id'),
                'subject': email.get('subject', 'No Subject'),
                'sender': email.get('from', 'Unknown Sender'),
                'to': email.get('to', 'Unknown Recipient'),
                'date': email.get('date', 'Unknown Date'),
                'body': email.get('body', '')
            }
            
            logger.info(f"Retrieved mock email content for ID {message_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting mock email content: {e}")
            return None
    
    def reply_to_email(self, message_id, body):
        """Reply to an email (mocked)"""
        try:
            # Find the original email in our mock data
            original_email = next((e for e in self.mock_emails if e.get('id') == message_id), None)
            
            if not original_email:
                logger.error(f"Mock email with ID {message_id} not found")
                return {
                    'success': False,
                    'error': f"Email with ID {message_id} not found"
                }
            
            # Get original email details
            sender = original_email.get('from', 'Unknown Sender')
            subject = original_email.get('subject', 'No Subject')
            thread_id = original_email.get('threadId', f"thread_{random.randint(1, 10)}")
            
            # Prepare reply subject
            if not subject.startswith('Re:'):
                subject = f"Re: {subject}"
            
            # Create a new mock email as the reply
            new_email_id = f"email_{len(self.mock_emails) + 1}"
            
            reply_email = {
                "id": new_email_id,
                "threadId": thread_id,  # Same thread as original
                "from": "me@example.com",
                "to": sender,
                "subject": subject,
                "body": body,
                "date": datetime.now().isoformat(),
                "read": True,
                "labels": ["SENT"],
                "in_reply_to": message_id
            }
            
            # Add to mock emails
            self.mock_emails.append(reply_email)
            
            logger.info(f"Mock reply sent to {sender} with subject '{subject}'")
            
            return {
                'success': True,
                'message_id': new_email_id
            }
            
        except Exception as e:
            logger.error(f"Error sending mock reply: {e}")
            return {
                'success': False,
                'error': str(e)
            }
