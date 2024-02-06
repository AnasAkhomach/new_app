# surgery_staff_assignment_service.py

from pymongo.errors import PyMongoError
# Import the necessary class from models.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import SurgeryStaffAssignment


class SurgeryStaffAssignmentService:
    @staticmethod
    def create_surgery_staff_assignment(assignment_data):
        """Creates a new surgery staff assignment."""
        try:
            document = assignment_data.to_document()
            db.surgery_staff_assignments.insert_one(document)
            print(f"Surgery staff assignment {document['assignment_id']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating surgery staff assignment: {e}")

    @staticmethod
    def update_surgery_staff_assignment(assignment_id, update_fields):
        """Updates an existing surgery staff assignment."""
        try:
            result = db.surgery_staff_assignments.update_one(
                {"assignment_id": assignment_id},
                {"$set": update_fields}
            )
            if result.modified_count:
                print(f"Surgery staff assignment {assignment_id} updated successfully.")
            else:
                print(f"No changes made to surgery staff assignment {assignment_id}.")
        except PyMongoError as e:
            print(f"Error updating surgery staff assignment: {e}")

    @staticmethod
    def delete_surgery_staff_assignment(assignment_id):
        """Deletes a surgery staff assignment."""
        try:
            result = db.surgery_staff_assignments.delete_one({"assignment_id": assignment_id})
            if result.deleted_count:
                print(f"Surgery staff assignment {assignment_id} deleted successfully.")
            else:
                print(f"Surgery staff assignment {assignment_id} not found.")
        except PyMongoError as e:
            print(f"Error deleting surgery staff assignment: {e}")

    @staticmethod
    def get_surgery_staff_assignment_by_id(assignment_id):
        try:
            document = db.surgery_staff_assignments.find_one({"assignment_id": assignment_id})
            return SurgeryStaffAssignment.from_document(document) if document else None
        except PyMongoError as e:
            print(f"Error retrieving surgery staff assignment: {e}")

# Example usage
if __name__ == "__main__":
    # Example surgery staff assignment data
    new_assignment = SurgeryStaffAssignment("ASSIGN001", "SURG001", "STAFF001", "Lead Surgeon")
    
    # Create a new assignment
    SurgeryStaffAssignmentService.create_surgery_staff_assignment(new_assignment)
    
    # Update an existing assignment
    SurgeryStaffAssignmentService.update_surgery_staff_assignment("ASSIGN001", {"role": "Assistant Surgeon"})
    
    # Delete an assignment
    SurgeryStaffAssignmentService.delete_surgery_staff_assignment("ASSIGN001")
