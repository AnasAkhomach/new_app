"""Service layer for managing staff in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import Staff


class StaffService:
    """Provides services for managing staff."""

    @staticmethod
    def create_staff(db, staff_data):  # Added db parameter
        """Creates a new staff record."""
        try:
            new_staff = Staff(
                name=staff_data["name"],
                role=staff_data["role"],
                contact_info=staff_data.get("contact_info"),
                specialization=staff_data.get("specialization"),
                availability=staff_data.get("availability", True),
            )
            db.add(new_staff)
            db.commit()
            db.refresh(new_staff)  # Added refresh
            print(f"Staff {new_staff.name} created successfully.")
            return new_staff.staff_id  # Added return ID
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating staff: {e}")
            return None  # Added return None on error

    @staticmethod
    def get_staff(db, staff_id):  # Added db parameter
        """Retrieves a staff by staff_id and returns a Staff instance."""
        try:
            staff = db.query(Staff).filter_by(staff_id=staff_id).first()
            if staff:
                return staff
            print(f"No staff found with ID {staff_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error retrieving staff: {e}")
            return None

    @staticmethod
    def update_staff(db, staff_id, update_fields):  # Added db parameter
        """Updates an existing staff record."""
        try:
            result = db.query(Staff).filter_by(staff_id=staff_id).update(update_fields)
            db.commit()
            if result:
                print(f"Staff {staff_id} updated successfully.")
                return True  # Added return True
            print(f"No staff found with ID {staff_id} or no new data to update.")
            return False  # Added return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating staff: {e}")
            return False  # Added return False on error

    @staticmethod
    def delete_staff(db, staff_id):  # Added db parameter
        """Deletes a staff record."""
        try:
            result = db.query(Staff).filter_by(staff_id=staff_id).delete()
            db.commit()
            if result:
                print(f"Staff {staff_id} deleted successfully.")
                return True  # Added return True
            print(f"No staff found with ID {staff_id}.")
            return False  # Added return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting staff: {e}")
            return False  # Added return False on error
