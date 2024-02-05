# Import necessary modules and services
from calendar_service import CalendarService
from notification_service import notification_service
from pymongo.errors import PyMongoError
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import Surgery

# Initialize logging
logger = logging.getLogger(__name__)

class SurgeryService:
    def __init__(self):
        self.calendar_service = CalendarService()

    @staticmethod
    def create_surgery(surgery_data):
        """Creates a new surgery record in the database."""
        try:
            document = surgery_data.to_document()
            result = db.surgeries.insert_one(document)
            print(f"Surgery {document['surgery_id']} created successfully with ID {result.inserted_id}.")
            return result.inserted_id
        except PyMongoError as e:
            logger.error(f"Error creating surgery: {e}")
            return None

    @staticmethod
    def update_surgery(surgery_id, update_fields):
        """Updates an existing surgery record."""
        try:
            result = db.surgeries.update_one({"surgery_id": surgery_id}, {"$set": update_fields})
            if result.modified_count:
                logger.info(f"Surgery {surgery_id} updated successfully.")
            else:
                logger.warning(f"No changes made to surgery {surgery_id}.")
        except PyMongoError as e:
            logger.error(f"Error updating surgery: {e}")

    @staticmethod
    def delete_surgery(surgery_id):
        """Deletes a surgery record."""
        try:
            result = db.surgeries.delete_one({"surgery_id": surgery_id})
            if result.deleted_count:
                logger.info(f"Surgery {surgery_id} deleted successfully.")
            else:
                logger.warning(f"Surgery {surgery_id} not found.")
        except PyMongoError as e:
            logger.error(f"Error deleting surgery: {e}")

    def schedule_surgery(self, surgeon, surgery_details):
        """Schedules a surgery, updates the surgeon's calendar, and sends notifications."""
        try:
            surgery_id = self.create_surgery(surgery_details)
            if not surgery_id:
                raise Exception("Failed to save surgery to database.")
            
            self.calendar_service.update_surgeon_calendar(surgeon, None, surgery_details)
            notification_service.send_notification(
                recipient_email=surgeon['email'],
                subject="New Surgery Scheduled",
                body=f"A new surgery {surgery_details['surgery_type']} has been scheduled for {surgery_details['start_time']}."
            )
            logger.info("Surgery successfully scheduled and notifications sent.")
            return "Surgery successfully scheduled and notifications sent."
        except Exception as e:
            logger.error(f"Error scheduling surgery: {e}")
            return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    surgery_service = SurgeryService()
    surgeon = {'name': 'Dr. Smith', 'email': 'dr.smith@example.com', 'calendar_id': 'surgeon_calendar_id'}
    surgery_details = {
        'surgery_id': 'SURG004',  # Ensure this ID is unique
        'patient_id': 'PAT001',
        'scheduled_date': '2023-01-02T09:00:00',
        'surgery_type': 'Cardiothoracic',
        'urgency_level': 'High',
        'duration': 180,
        'status': 'Scheduled'
    }
    result = surgery_service.schedule_surgery(surgeon, surgery_details)
    print(result)
