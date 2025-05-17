"""Service layer for managing surgeon preferences in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import SurgeonPreference


class SurgeonPreferenceService:
    """Provides services for managing surgeon preferences."""

    @staticmethod
    def create_surgeon_preference(db, pref_data): # Added db parameter
        """Creates a new surgeon preference."""
        try:
            new_pref = SurgeonPreference(**pref_data)
            db.add(new_pref)
            db.commit()
            db.refresh(new_pref) # Added refresh
            print(f"Surgeon preference {new_pref.preference_id} created successfully.")
            return new_pref.preference_id # Return ID
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating surgeon preference: {e}")
            return None # Return None on error

    @staticmethod
    def get_surgeon_preference(db, preference_id): # Added db parameter
        """Fetches a surgeon preference by its ID."""
        try:
            preference = (
                db.query(SurgeonPreference)
                .filter_by(preference_id=preference_id)
                .first()
            )
            if preference:
                return preference
            print(f"Surgeon preference {preference_id} not found.")
            return None
        except SQLAlchemyError as e:
            print(f"Error fetching surgeon preference: {e}")
            return None

    @staticmethod
    def update_surgeon_preference(db, preference_id, update_fields): # Added db parameter
        """Updates an existing surgeon preference."""
        try:
            result = (
                db.query(SurgeonPreference)
                .filter_by(preference_id=preference_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Surgeon preference {preference_id} updated successfully.")
                return True
            print(f"Surgeon preference {preference_id} not found or no new data to update.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating surgeon preference: {e}")
            return False

    @staticmethod
    def delete_surgeon_preference(db, preference_id): # Added db parameter
        """Deletes a surgeon preference."""
        try:
            result = (
                db.query(SurgeonPreference)
                .filter_by(preference_id=preference_id)
                .delete()
            )
            db.commit()
            if result:
                print(f"Surgeon preference {preference_id} deleted successfully.")
                return True
            print(f"Surgeon preference {preference_id} not found.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting surgeon preference: {e}")
            return False
