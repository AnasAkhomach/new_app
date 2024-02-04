from calendar_service import CalendarService
from notification_service import notification_service
import logging
from models import Surgeon, Surgery

# Initialize logging
logger = logging.getLogger(__name__)

class SurgeryService:
    def __init__(self):
        self.calendar_service = CalendarService()

    def schedule_surgery(self, surgeon, surgery_details):
        """
        Schedules a surgery, updates the surgeon's calendar, and sends notifications.
        
        Args:
            surgeon (dict): Information about the surgeon.
            surgery_details (dict): Details of the surgery to be scheduled.
            
        Returns:
            A message indicating the outcome of the scheduling attempt.
        """
        try:
            # Step 1: Save the surgery details to your database
            surgery_id = self.save_surgery_to_database(surgeon, surgery_details)
            if not surgery_id:
                raise Exception("Failed to save surgery to database.")
            
            # Step 2: Update the surgeon's calendar
            # Ensure CalendarService has been authenticated properly before this step
            self.calendar_service.update_surgeon_calendar(surgeon, None, surgery_details)

            # Step 3: Send notification about the new surgery
            # Ensure NotificationService has necessary permissions and is configured correctly
            notification_service.send_notification(
                recipient_email=surgeon['email'],
                subject="New Surgery Scheduled",
                body=f"A new surgery {surgery_details['surgery_type']} has been scheduled for {surgery_details['start_time']}."
            )
            return "Surgery successfully scheduled and notifications sent."
        
        except Exception as e:
            logger.error(f"Error scheduling surgery: {e}")
            return f"An error occurred: {e}"

    def save_surgery_to_database(self, surgeon, surgery_details):
        """
        Placeholder function to save surgery to a database. Actual implementation will vary.
        """
        # Simulate database save operation
        # In real implementation, interact with your database here and handle any potential errors
        return "surgery123"  # Simulated surgery ID or object

    def update_surgery_in_database(self, surgery_id, surgery_details):
        """
        Updates surgery details in a database. Actual implementation will vary.
        
        Args:
            surgery_id (int): ID of the surgery to update.
            surgery_details (dict): New details for the surgery.
            
        Returns:
            Surgery: The updated Surgery object, or None if the update fails.
        """
        # Simulate database update operation
        # In real implementation, interact with your ORM or database interface here
        # Return the updated Surgery object or None on failure
        return Surgery(surgery_id, **surgery_details)  # Assuming a Surgery class exists


    def modify_surgery(self, surgeon, original_surgery, updated_surgery_details):
        """
        Modifies details of an existing surgery, updates the surgeon's calendar, and sends notifications.
        
        Args:
            surgeon (Surgeon): The surgeon performing the surgery, expected to be a Surgeon object.
            original_surgery (Surgery): Original details of the surgery, expected to be a Surgery object.
            updated_surgery_details (dict): Updated details of the surgery.
            
        Returns:
            str: Outcome message.
        """
        try:
            # Validate inputs
            if not isinstance(surgeon, Surgeon) or not isinstance(original_surgery, Surgery):
                raise ValueError("Invalid surgeon or surgery object.")

            # Step 1: Update the surgery details in your database
            updated_surgery = self.update_surgery_in_database(original_surgery.id, updated_surgery_details)
            if not updated_surgery:
                raise Exception("Failed to update surgery in database.")

            # Step 2: Update the surgeon's calendar
            # This step might need to remove the old event and add a new one based on updated details
            self.calendar_service.update_surgeon_calendar(surgeon, original_surgery, updated_surgery_details)

            # Step 3: Send notification about the surgery update
            notification_service.send_notification(
                recipient_email=surgeon.email,  # Assuming Surgeon model has an email attribute
                subject="Surgery Details Updated",
                body=f"Details for your surgery scheduled on {original_surgery.start_time} have been updated to {updated_surgery_details['start_time']}."
            )
            return "Surgery successfully modified and notifications sent."
        
        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            return f"Input validation error: {ve}"
        except Exception as e:
            logger.error(f"Error modifying surgery: {e}")
            return f"An error occurred: {e}"



# Example usage (assuming this runs in a context where surgeon and surgery_details are defined)
if __name__ == "__main__":
    surgery_service = SurgeryService()
    surgeon = {'name': 'Dr. Smith', 'email': 'dr.smith@example.com', 'calendar_id': 'surgeon_calendar_id'}
    surgery_details = {
        'surgery_type': 'Appendectomy',
        'start_time': '2023-10-01T09:00:00Z',
        'duration': 2  # hours
    }
    result = surgery_service.schedule_surgery(surgeon, surgery_details)
    print(result)

