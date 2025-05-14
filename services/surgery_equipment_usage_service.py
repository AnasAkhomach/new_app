# surgery_equipment_usage_service.py

from pymongo.errors import PyMongoError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import SurgeryEquipmentUsage


class SurgeryEquipmentUsageService:
    @staticmethod
    def create_surgery_equipment_usage(usage_data):
        """Creates a new surgery equipment usage record."""
        try:
            document = usage_data.to_document()
            db.surgery_equipment_usage.insert_one(document)
            print(f"Surgery equipment usage {document['usage_id']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating surgery equipment usage: {e}")

    @staticmethod
    def update_surgery_equipment_usage(usage_id, update_fields):
        """Updates an existing surgery equipment usage record."""
        try:
            result = db.surgery_equipment_usage.update_one(
                {"usage_id": usage_id},
                {"$set": update_fields}
            )
            if result.modified_count:
                print(f"Surgery equipment usage {usage_id} updated successfully.")
            else:
                print(f"No changes made to surgery equipment usage {usage_id}.")
        except PyMongoError as e:
            print(f"Error updating surgery equipment usage: {e}")

    @staticmethod
    def delete_surgery_equipment_usage(usage_id):
        """Deletes a surgery equipment usage record."""
        try:
            result = db.surgery_equipment_usage.delete_one({"usage_id": usage_id})
            if result.deleted_count:
                print(f"Surgery equipment usage {usage_id} deleted successfully.")
            else:
                print(f"Surgery equipment usage {usage_id} not found.")
        except PyMongoError as e:
            print(f"Error deleting surgery equipment usage: {e}")

    @staticmethod
    def get_usage(usage_id):
        """Fetches an equipment usage by its ID."""
        try:
            document = db.surgery_equipment_usage.find_one({"usage_id": usage_id})
            if document:
                return SurgeryEquipmentUsage.from_document(document)
            else:
                print("Equipment usage not found.")
                return None
        except PyMongoError as e:
            print(f"Error fetching equipment usage: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Example surgery equipment usage data initialization
    new_usage = SurgeryEquipmentUsage("USAGE001", "SURG003", "EQUIP001")
    
    # Create a new equipment usage
    SurgeryEquipmentUsageService.create_surgery_equipment_usage(new_usage)
    
    # Update an existing equipment usage
    SurgeryEquipmentUsageService.update_surgery_equipment_usage("USAGE001", {"equipment_id": "EQUIP002"})
    
    # Delete an equipment usage record
    SurgeryEquipmentUsageService.delete_surgery_equipment_usage("USAGE001")
