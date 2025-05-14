# staff_assignment_service.py

from pymongo.errors import PyMongoError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from bson.objectid import ObjectId
from models import StaffAssignment


class StaffAssignmentService:
    @staticmethod
    def add_staff_assignment(surgery_appointment_id, staff_id, role):
        """Adds a new staff assignment to an existing surgery appointment."""
        try:
            surgery_appointment_oid = ObjectId(surgery_appointment_id)
            update_result = db.surgery_appointments.update_one(
                {"_id": surgery_appointment_oid},
                {"$push": {"staff_assignments": {"staff_id": staff_id, "role": role}}}
            )
            if update_result.modified_count:
                print("Staff assignment added successfully to the surgery appointment.")
            else:
                print("Surgery appointment not found or staff assignment already exists.")
        except PyMongoError as e:
            print(f"Error adding staff assignment due to a database issue: {e}")

    @staticmethod
    def update_staff_role(surgery_appointment_id, staff_id, new_role):
        """Updates the role of a specific staff assignment within a surgery appointment."""
        try:
            surgery_appointment_oid = ObjectId(surgery_appointment_id)
            update_result = db.surgery_appointments.update_one(
                {"_id": surgery_appointment_oid, "staff_assignments.staff_id": staff_id},
                {"$set": {"staff_assignments.$.role": new_role}}
            )
            if update_result.modified_count:
                print("Staff assignment role updated successfully.")
            else:
                print("Surgery appointment or staff assignment not found.")
        except PyMongoError as e:
            print(f"Error updating staff role due to a database issue: {e}")

    @staticmethod
    def remove_staff_assignment(surgery_appointment_id, staff_id):
        """Removes a specific staff assignment from a surgery appointment."""
        try:
            surgery_appointment_oid = ObjectId(surgery_appointment_id)
            update_result = db.surgery_appointments.update_one(
                {"_id": surgery_appointment_oid},
                {"$pull": {"staff_assignments": {"staff_id": staff_id}}}
            )
            if update_result.modified_count:
                print("Staff assignment removed successfully from the surgery appointment.")
            else:
                print("Surgery appointment or staff assignment not found.")
        except PyMongoError as e:
            print(f"Error removing staff assignment due to a database issue: {e}")

    @staticmethod
    def get_staff_assignment(assignment_id):
        """Fetches a staff assignment by its ID."""
        try:
            document = db.staff_assignments.find_one({"assignment_id": assignment_id})
            if document:
                return StaffAssignment.from_document(document)
            else:
                print("Staff assignment not found.")
                return None
        except PyMongoError as e:
            print(f"Error fetching staff assignment: {e}")
            return None

# Example usage of the StaffAssignmentService
if __name__ == "__main__":
    # These IDs are placeholders. Replace them with actual values from your database.
    surgery_appointment_id = "5f8d0d55b54764421b7156cd"  # Example ObjectID string
    staff_id = "staff123"
    role = "Nurse"
    new_role = "Lead Surgeon"

    # Demonstrating adding, updating, and removing a staff assignment
    StaffAssignmentService.add_staff_assignment(surgery_appointment_id, staff_id, role)
    StaffAssignmentService.update_staff_role(surgery_appointment_id, staff_id, new_role)
    StaffAssignmentService.remove_staff_assignment(surgery_appointment_id, staff_id)
