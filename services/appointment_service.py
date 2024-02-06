from pymongo.errors import PyMongoError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db

from models import SurgeryAppointment, StaffAssignment
from datetime import datetime

class AppointmentService:
    @staticmethod
    def create_surgery_appointment(appointment_id, surgery_id, patient_id, staff_assignments_info, room_id, start_time, end_time):
        """
        Creates a new surgery appointment and saves it to the MongoDB database.
        """
        try:
            # Validation placeholder (you'll need to implement the actual validation logic)
            if not AppointmentService.validate_appointment(room_id, start_time, end_time, staff_assignments_info):
                print("Validation failed. Appointment cannot be scheduled.")
                return False

            staff_assignments = [StaffAssignment(staff_id=sa['staff_id'], role=sa['role']) for sa in staff_assignments_info]
            
            new_appointment = SurgeryAppointment(
                appointment_id=appointment_id,
                surgery_id=surgery_id,
                patient_id=patient_id,
                staff_assignments=staff_assignments,
                room_id=room_id,
                start_time=start_time,
                end_time=end_time
            )
            
            db.surgery_appointments.insert_one(new_appointment.to_document())
            print(f"Surgery appointment {appointment_id} created successfully.")
            return True
        except PyMongoError as e:
            print(f"Failed to create surgery appointment due to database error: {e}")
            return False

    @staticmethod
    def validate_appointment(room_id, start_time, end_time, staff_assignments_info):
        """
        Validates whether a surgery appointment can be scheduled without conflicts.
        """
        try:
            # Convert start and end times to datetime objects if in string format
            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

            if not AppointmentService.is_room_available(room_id, start_time, end_time):
                print("Room is not available.")
                return False

            for staff_info in staff_assignments_info:
                staff_id = staff_info['staff_id']
                if not AppointmentService.is_staff_available(staff_id, start_time, end_time):
                    print(f"Staff member {staff_id} is not available.")
                    return False
            
            return True
        except PyMongoError as e:
            print(f"Database error during validation: {e}")
            return False

    @staticmethod
    def is_room_available(room_id, start_time, end_time):
        """Checks if the room is available for the given time slot."""
        try:
            count = db.surgery_appointments.count_documents({
                "room_id": room_id,
                "$or": [
                    {"start_time": {"$lt": end_time, "$gte": start_time}},
                    {"end_time": {"$gt": start_time, "$lte": end_time}}
                ]
            })
            return count == 0
        except PyMongoError as e:
            print(f"Database error checking room availability: {e}")
            return False

    @staticmethod
    def is_staff_available(staff_id, start_time, end_time):
        """Checks if the staff member is available for the given time slot."""
        try:
            count = db.surgery_appointments.count_documents({
                "staff_assignments": {"$elemMatch": {"staff_id": staff_id}},
                "$or": [
                    {"start_time": {"$lt": end_time, "$gte": start_time}},
                    {"end_time": {"$gt": start_time, "$lte": end_time}}
                ]
            })
            return count == 0
        except PyMongoError as e:
            print(f"Database error checking staff availability: {e}")
            return False

    @staticmethod
    def get_appointment_by_id(appointment_id):
        """Retrieves a surgery appointment by its ID."""
        try:
            document = db.surgery_appointments.find_one({"appointment_id": appointment_id})
            return SurgeryAppointment.from_document(document) if document else None
        except PyMongoError as e:
            print(f"Error retrieving appointment: {e}")
            return None
        
    @staticmethod
    def update_appointment(appointment_id, update_data):
        """Updates an existing surgery appointment."""
        try:
            db.surgery_appointments.update_one(
                {"appointment_id": appointment_id},
                {"$set": update_data}
            )
            print(f"Appointment {appointment_id} updated successfully.")
        except PyMongoError as e:
            print(f"Error updating appointment: {e}")

    @staticmethod
    def delete_appointment(appointment_id):
        """Deletes a surgery appointment."""
        try:
            db.surgery_appointments.delete_one({"appointment_id": appointment_id})
            print(f"Appointment {appointment_id} deleted successfully.")
        except PyMongoError as e:
            print(f"Error deleting appointment: {e}")

# Example usage
if __name__ == "__main__":
    # Example to create a new appointment
    new_appointment = SurgeryAppointment(
        "APPT001", "SUR001", "P001", 
        [{"staff_id": "STAFF001", "role": "Lead Surgeon"}], 
        "OR001", "2023-08-01T09:00:00", "2023-08-01T11:00:00"
    )
    #AppointmentService.create_surgery_appointment(new_appointment)
    AppointmentService.create_surgery_appointment("APPT001", "SUR001", "P001", [{"staff_id": "STAFF001", "role": "Lead Surgeon"}], "OR001", "2023-08-01T09:00:00", "2023-08-01T11:00:00")
