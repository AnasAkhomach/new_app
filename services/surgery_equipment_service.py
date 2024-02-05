# surgery_equipment_service.py

from pymongo.errors import PyMongoError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import SurgeryEquipment

class SurgeryEquipmentService:
    @staticmethod
    def create_surgery_equipment(equipment_data):
        """Creates a new surgery equipment record."""
        try:
            document = equipment_data.to_document()
            db.surgery_equipment.insert_one(document)
            print(f"Surgery equipment {document['equipment_id']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating surgery equipment: {e}")

    @staticmethod
    def update_surgery_equipment(equipment_id, update_fields):
        """Updates an existing surgery equipment record."""
        try:
            result = db.surgery_equipment.update_one(
                {"equipment_id": equipment_id},
                {"$set": update_fields}
            )
            if result.modified_count:
                print(f"Surgery equipment {equipment_id} updated successfully.")
            else:
                print(f"No changes made to surgery equipment {equipment_id}.")
        except PyMongoError as e:
            print(f"Error updating surgery equipment: {e}")

    @staticmethod
    def delete_surgery_equipment(equipment_id):
        """Deletes a surgery equipment record."""
        try:
            result = db.surgery_equipment.delete_one({"equipment_id": equipment_id})
            if result.deleted_count:
                print(f"Surgery equipment {equipment_id} deleted successfully.")
            else:
                print(f"Surgery equipment {equipment_id} not found.")
        except PyMongoError as e:
            print(f"Error deleting surgery equipment: {e}")

# Example usage
if __name__ == "__main__":
    # Example surgery equipment data initialization
    new_equipment = SurgeryEquipment("EQUIP003", "Laser Scalpel", "Cutting", True)
    
    # Create a new equipment record
    SurgeryEquipmentService.create_surgery_equipment(new_equipment)
    
    # Update an existing equipment record
    SurgeryEquipmentService.update_surgery_equipment("EQUIP003", {"availability": False})
    
    # Delete an equipment record
    SurgeryEquipmentService.delete_surgery_equipment("EQUIP003")
