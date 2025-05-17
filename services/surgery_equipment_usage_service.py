"""Service layer for managing surgery equipment usage in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import SurgeryEquipmentUsage


class SurgeryEquipmentUsageService:
    """Provides services for managing surgery equipment usage."""

    @staticmethod
    def create_surgery_equipment_usage(db, usage_data):  # Added db parameter
        """Creates a new surgery equipment usage record."""
        try:
            new_usage = SurgeryEquipmentUsage(
                surgery_id=usage_data["surgery_id"],
                equipment_id=usage_data["equipment_id"],
                usage_start_time=usage_data.get(
                    "usage_start_time"
                ),  # Added usage_start_time
                usage_end_time=usage_data.get("usage_end_time"),  # Added usage_end_time
            )
            db.add(new_usage)
            db.commit()
            db.refresh(new_usage)  # Added refresh
            print(f"Surgery equipment usage {new_usage.usage_id} created successfully.")
            return new_usage.usage_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating surgery equipment usage: {e}")
            return None

    @staticmethod
    def update_surgery_equipment_usage(db, usage_id, update_fields):
        """Updates an existing surgery equipment usage record."""
        try:
            result = (
                db.query(SurgeryEquipmentUsage)
                .filter_by(usage_id=usage_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Equipment usage {usage_id} updated successfully.")
                return True
            print(
                f"No equipment usage found with ID {usage_id} or no new data to update."
            )
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating equipment usage: {e}")
            return False

    @staticmethod
    def delete_surgery_equipment_usage(db, usage_id):
        """Deletes a surgery equipment usage record."""
        try:
            result = (
                db.query(SurgeryEquipmentUsage).filter_by(usage_id=usage_id).delete()
            )
            db.commit()
            if result:
                print(f"Equipment usage {usage_id} deleted successfully.")
                return True
            print(f"No equipment usage found with ID {usage_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting equipment usage: {e}")
            return False

    @staticmethod
    def get_usage(db, usage_id):
        """Retrieves a surgery equipment usage record by usage_id and returns a SurgeryEquipmentUsage instance."""
        try:
            usage = db.query(SurgeryEquipmentUsage).filter_by(usage_id=usage_id).first()
            if usage:
                return usage
            print(f"No equipment usage found with ID {usage_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error retrieving equipment usage: {e}")
            return None
