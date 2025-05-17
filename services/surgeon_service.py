"""Service layer for managing surgeons in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import Surgeon


class SurgeonService:
    """Provides services for managing surgeons."""

    @staticmethod
    def create_surgeon(db, surgeon_data):  # Added db parameter
        """Creates a new surgeon record."""
        try:
            new_surgeon = Surgeon(
                name=surgeon_data["name"],
                contact_info=surgeon_data.get("contact_info"),
                specialization=surgeon_data["specialization"],
                credentials=surgeon_data["credentials"],
                availability=surgeon_data.get("availability", True),
            )
            db.add(new_surgeon)
            db.commit()
            db.refresh(new_surgeon)  # Added refresh
            print(f"Surgeon {new_surgeon.name} created successfully.")
            return new_surgeon.surgeon_id  # Added return ID
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating surgeon: {e}")
            return None  # Added return None on error

    @staticmethod
    def get_surgeon(db, surgeon_id):  # Added db parameter
        """Retrieves a surgeon by surgeon_id and returns a Surgeon instance."""
        try:
            surgeon = db.query(Surgeon).filter_by(surgeon_id=surgeon_id).first()
            if surgeon:
                return surgeon
            print(f"No surgeon found with ID {surgeon_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error retrieving surgeon: {e}")
            return None

    @staticmethod
    def update_surgeon(db, surgeon_id, update_fields):  # Added db parameter
        """Updates an existing surgeon record."""
        try:
            result = (
                db.query(Surgeon).filter_by(surgeon_id=surgeon_id).update(update_fields)
            )
            db.commit()
            if result:
                print(f"Surgeon {surgeon_id} updated successfully.")
                return True  # Added return True
            print(
                f"No surgeon found with ID {surgeon_id} or no new data to update."
            )
            return False  # Added return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating surgeon: {e}")
            return False  # Added return False on error

    @staticmethod
    def delete_surgeon(db, surgeon_id):  # Added db parameter
        """Deletes a surgeon record."""
        try:
            result = db.query(Surgeon).filter_by(surgeon_id=surgeon_id).delete()
            db.commit()
            if result:
                print(f"Surgeon {surgeon_id} deleted successfully.")
                return True  # Added return True
            print(f"No surgeon found with ID {surgeon_id}.")
            return False  # Added return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting surgeon: {e}")
            return False  # Added return False on error
