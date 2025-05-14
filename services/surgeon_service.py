# surgeon_service.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import Surgeon
from pymongo.errors import PyMongoError


class SurgeonService:
    @staticmethod
    def create_surgeon(surgeon_data):
        """Creates a new surgeon record."""
        try:
            document = surgeon_data.to_document()
            db.surgeons.insert_one(document)
            print(f"Surgeon {document['name']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating surgeon: {e}")

    @staticmethod
    def get_surgeon(staff_id):
        """Retrieves a surgeon by staff_id and returns a Surgeon instance."""
        try:
            document = db.surgeons.find_one({"staff_id": staff_id})
            if document:
                return Surgeon.from_document(document)
            else:
                print(f"No surgeon found with ID {staff_id}")
                return None
        except PyMongoError as e:
            print(f"Error retrieving surgeon: {e}")
            return None

    @staticmethod
    def update_surgeon(staff_id, update_fields):
        """Updates an existing surgeon record."""
        try:
            db.surgeons.update_one({"staff_id": staff_id}, {"$set": update_fields})
            print(f"Surgeon {staff_id} updated successfully.")
        except PyMongoError as e:
            print(f"Error updating surgeon: {e}")

    @staticmethod
    def delete_surgeon(staff_id):
        """Deletes a surgeon record."""
        try:
            db.surgeons.delete_one({"staff_id": staff_id})
            print(f"Surgeon {staff_id} deleted successfully.")
        except PyMongoError as e:
            print(f"Error deleting surgeon: {e}")

# Example usage
if __name__ == "__main__":
    try:
        new_surgeon = Surgeon("SURGEON001", "Dr. Alex", "Surgeon", "alex@example.com", ["Cardiology"], [("2023-01-01", "2023-12-31")])
        SurgeonService.create_surgeon(new_surgeon)
    except Exception as e:
        print(f"An error occurred: {e}")
