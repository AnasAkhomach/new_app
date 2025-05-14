from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self):
        # Assumes 'token.json' is obtained after the OAuth flow
        self.credentials = Credentials.from_authorized_user_file('token.json')
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def update_surgeon_calendar(self, surgeon, original_surgery, new_surgery):
        try:
            # Step 1: Delete the original surgery event if it exists
            if hasattr(original_surgery, 'calendar_event_id'):
                self.service.events().delete(calendarId=surgeon.calendar_id,
                                             eventId=original_surgery.calendar_event_id).execute()
                logger.info(f"Original surgery event {original_surgery.surgery_id} deleted.")

            # Step 2: Create a new event for the new surgery
            event = {
                'summary': f'Surgery: {new_surgery.surgery_type}',
                'description': f'Surgery details. Patient ID: {new_surgery.patient_id}',
                'start': {'dateTime': new_surgery.start_time.isoformat(), 'timeZone': 'America/New_York'},
                'end': {'dateTime': (new_surgery.start_time + timedelta(hours=new_surgery.duration)).isoformat(), 'timeZone': 'America/New_York'},
            }
            created_event = self.service.events().insert(calendarId=surgeon.calendar_id, body=event).execute()
            logger.info(f"New surgery event {new_surgery.surgery_id} added to calendar.")

        except Exception as e:
            logger.error(f"Error updating calendar for surgeon {surgeon.name}: {e}")
            # Consider retry logic or alternative handling here
