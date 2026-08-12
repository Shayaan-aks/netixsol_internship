import os
import datetime
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from src.config.settings import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    """Enterprise Google Calendar Integration with Service Account."""
    
    def __init__(self):
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        self.service = None
        self._authenticate()
        
    def _authenticate(self):
        # Fallback to mock if credentials don't exist yet, so pipeline doesn't crash on boot
        if os.path.exists(self.credentials_path):
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            self.service = build('calendar', 'v3', credentials=creds)
        else:
            print(f"Warning: {self.credentials_path} not found. Running in Mock Calendar Mode.")

    def check_availability(self, start_time: datetime.datetime, end_time: datetime.datetime) -> bool:
        """Checks if there are conflicts in the calendar."""
        if not self.service:
            return True # Mock always available
            
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True
        ).execute()
        
        events = events_result.get('items', [])
        return len(events) == 0

    def create_event(self, title: str, start_time: datetime.datetime, duration_minutes: int, description: str) -> Optional[str]:
        """Creates an event and returns the Event ID."""
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
        
        if not self.check_availability(start_time, end_time):
            raise ValueError("Time slot is not available. Conflict detected.")
            
        if not self.service:
            print(f"MOCK: Created event '{title}' at {start_time}")
            return "mock_event_id_123"

        event = {
            'summary': title,
            'description': description,
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Karachi'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Karachi'},
            'conferenceData': {
                'createRequest': {'requestId': f"{start_time.timestamp()}"}
            }
        }

        try:
            created_event = self.service.events().insert(
                calendarId='primary', body=event, conferenceDataVersion=1
            ).execute()
            return created_event.get('id')
        except Exception as e:
            print(f"Calendar API Error: {e}")
            return None
            
    def delete_event(self, event_id: str):
        if not self.service:
            print(f"MOCK: Deleted event {event_id}")
            return True
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except Exception as e:
            print(f"Calendar API Error: {e}")
            return False
