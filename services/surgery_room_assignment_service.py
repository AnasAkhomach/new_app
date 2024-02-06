# surgery_room_assignment_service.py

from pymongo.errors import PyMongoError
import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import SurgeryRoomAssignment


class SurgeryRoomAssignmentService:
    @staticmethod
    def to_datetime(time_str):
        """Converts string to datetime object."""
        return datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def create_surgery_room_assignment(assignment_data):
        """Creates a new surgery room assignment."""
        try:
            document = assignment_data.to_document()
            # Ensure start_time and end_time are datetime objects
            document['start_time'] = SurgeryRoomAssignmentService.to_datetime(document['start_time'])
            document['end_time'] = SurgeryRoomAssignmentService.to_datetime(document['end_time'])
            db.surgery_room_assignments.insert_one(document)
            print(f"Surgery room assignment {document['assignment_id']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating surgery room assignment: {e}")

    @staticmethod
    def update_surgery_room_assignment(assignment_id, update_fields):
        """Updates an existing surgery room assignment."""
        try:
            # Convert start_time and end_time to datetime if they are being updated
            if 'start_time' in update_fields:
                update_fields['start_time'] = SurgeryRoomAssignmentService.to_datetime(update_fields['start_time'])
            if 'end_time' in update_fields:
                update_fields['end_time'] = SurgeryRoomAssignmentService.to_datetime(update_fields['end_time'])

            result = db.surgery_room_assignments.update_one(
                {"assignment_id": assignment_id},
                {"$set": update_fields}
            )
            if result.modified_count:
                print(f"Surgery room assignment {assignment_id} updated successfully.")
            else:
                print(f"No changes made to surgery room assignment {assignment_id}.")
        except PyMongoError as e:
            print(f"Error updating surgery room assignment: {e}")

    @staticmethod
    def delete_surgery_room_assignment(assignment_id):
        """Deletes a surgery room assignment."""
        try:
            result = db.surgery_room_assignments.delete_one({"assignment_id": assignment_id})
            if result.deleted_count:
                print(f"Surgery room assignment {assignment_id} deleted successfully.")
            else:
                print(f"Surgery room assignment {assignment_id} not found.")
        except PyMongoError as e:
            print(f"Error deleting surgery room assignment: {e}")

    @staticmethod
    def get_assignment(assignment_id):
        """Fetches a room assignment by its ID."""
        try:
            document = db.surgery_room_assignments.find_one({"assignment_id": assignment_id})
            if document:
                return SurgeryRoomAssignment.from_document(document)
            else:
                print("Room assignment not found.")
                return None
        except PyMongoError as e:
            print(f"Error fetching room assignment: {e}")
            return None

# Example usage
if __name__ == "__main__":
    
    # Example surgery room assignment data initialization
    new_assignment = SurgeryRoomAssignment(
        "ASSIGN002", 
        "SURG002", 
        "ROOM001", 
        "2023-01-01T09:00:00",  # Correct format
        "2023-01-01T11:00:00"
    )    
    # Create a new assignment
    SurgeryRoomAssignmentService.create_surgery_room_assignment(new_assignment)
    
    # Example updates (assuming the fields to be updated are passed correctly)
    SurgeryRoomAssignmentService.update_surgery_room_assignment("ASSIGN002", {"room_id": "ROOM002", "start_time": "2023-01-02T09:00:00"})
    
    # Delete an assignment
    SurgeryRoomAssignmentService.delete_surgery_room_assignment("ASSIGN002")
    db.client.close()
