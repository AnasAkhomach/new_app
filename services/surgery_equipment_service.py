"""Service layer for managing surgery equipment in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import SurgeryEquipment


class SurgeryEquipmentService:
    """Provides services for managing surgery equipment."""

    @staticmethod
    def create_surgery_equipment(db, equipment_data):  # Added db parameter
        """Creates a new surgery equipment record."""
        try:
            new_equipment = SurgeryEquipment(
                name=equipment_data["name"],
                type=equipment_data["type"],
                availability=equipment_data.get("availability", True),
            )
            db.add(new_equipment)
            db.commit()
            db.refresh(new_equipment)  # Added refresh
            print(
                f"Surgery equipment {new_equipment.equipment_id} created successfully."
            )
            return new_equipment.equipment_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating surgery equipment: {e}")
            return None

    @staticmethod
    def update_surgery_equipment(db, equipment_id, update_fields):  # Added db parameter
        """Updates an existing surgery equipment record."""
        try:
            result = (
                db.query(SurgeryEquipment)
                .filter_by(equipment_id=equipment_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Surgery equipment {equipment_id} updated successfully.")
                return True  # Added return True
            print(f"No changes made to surgery equipment {equipment_id}.")
            return False  # Added return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating surgery equipment: {e}")
            return False  # Added return False on error

    @staticmethod
    def delete_surgery_equipment(db, equipment_id):  # Added db parameter
        """Deletes a surgery equipment record."""
        try:
            result = (
                db.query(SurgeryEquipment).filter_by(equipment_id=equipment_id).delete()
            )
            db.commit()
            if result:
                print(f"Surgery equipment {equipment_id} deleted successfully.")
                return True  # Added return True
            print(f"Surgery equipment {equipment_id} not found.")
            return False  # Added return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting surgery equipment: {e}")
            return False  # Added return False on error

    @staticmethod
    def get_equipment(db, equipment_id):  # Added db parameter
        """Fetches an equipment by its ID."""
        try:
            equipment = (
                db.query(SurgeryEquipment).filter_by(equipment_id=equipment_id).first()
            )
            if equipment:
                return equipment
            print("Equipment not found.")
            return None
        except SQLAlchemyError as e:
            print(f"Error fetching equipment: {e}")
            return None
