# surgeon_service.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import Surgeon


class SurgeonService:
    @staticmethod
    def create_surgeon(surgeon_data):
        """Creates a new surgeon record."""
        document = surgeon_data.to_document()
        db.surgeons.insert_one(document)
        print(f"Surgeon {document['name']} created successfully.")

    @staticmethod
    def update_surgeon(surgeon_id, update_fields):
        """Updates an existing surgeon record."""
        db.surgeons.update_one({"staff_id": surgeon_id}, {"$set": update_fields})
        print(f"Surgeon {surgeon_id} updated successfully.")

    @staticmethod
    def delete_surgeon(surgeon_id):
        """Deletes a surgeon record."""
        db.surgeons.delete_one({"staff_id": surgeon_id})
        print(f"Surgeon {surgeon_id} deleted successfully.")

# Example usage
if __name__ == "__main__":
    new_surgeon = Surgeon("SURG001", "Dr. Smith", "Surgeon", "dr.smith@example.com", "Cardiology", [("2023-01-01", "2023-12-31")])
    SurgeonService.create_surgeon(new_surgeon)

