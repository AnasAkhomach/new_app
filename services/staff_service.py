# staff_service.py

from pymongo.errors import PyMongoError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import Staff

class StaffService:
    @staticmethod
    def create_staff(staff_data):
        """Creates a new staff record."""
        try:
            document = staff_data.to_document()
            db.staff.insert_one(document)
            print(f"Staff {document['name']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating staff: {e}")

    @staticmethod
    def get_staff(staff_id):
        """Retrieves a staff by staff_id and returns a Staff instance."""
        try:
            document = db.staff.find_one({"staff_id": staff_id})
            if document:
                return Staff.from_document(document)
            else:
                print(f"No staff found with ID {staff_id}")
                return None
        except PyMongoError as e:
            print(f"Error retrieving staff: {e}")
            return None

    @staticmethod
    def update_staff(staff_id, update_fields):
        """Updates an existing staff record."""
        try:
            db.staff.update_one({"staff_id": staff_id}, {"$set": update_fields})
            print(f"Staff {staff_id} updated successfully.")
        except PyMongoError as e:
            print(f"Error updating staff: {e}")

    @staticmethod
    def delete_staff(staff_id):
        """Deletes a staff record."""
        try:
            db.staff.delete_one({"staff_id": staff_id})
            print(f"Staff {staff_id} deleted successfully.")
        except PyMongoError as e:
            print(f"Error deleting staff: {e}")

# Example usage
if __name__ == "__main__":
    try:
        new_staff = Staff("STAFF001", "John Doe", "Nurse", "contact@example.com", "Cardiology", [("2023-01-01", "2023-12-31")])
        StaffService.create_staff(new_staff)
    except Exception as e:
        print(f"An error occurred: {e}")
    @staticmethod
    def delete_staff(staff_id):
        """Deletes a staff record."""
        try:
            result = db.staff.delete_one({"staff_id": staff_id})
            if result.deleted_count:
                print(f"Staff {staff_id} deleted successfully.")
            else:
                print(f"Staff {staff_id} not found.")
        except PyMongoError as e:
            print(f"Error deleting staff: {e}")

# Example usage
if __name__ == "__main__":
    # Example staff data initialization
    #new_staff = Staff("STAFF004", "Jane Doe", "Nurse", "jane.doe@example.com", None, None)
    new_staff = Staff("STAFF004", "Jane Doe", "Nurse", "jane.doe@example.com")

    # Create a new staff record
    StaffService.create_staff(new_staff)
    
    # Update an existing staff record
    StaffService.update_staff("STAFF004", {"role": "Senior Nurse"})
    
    # Delete a staff record
    StaffService.delete_staff("STAFF004")
