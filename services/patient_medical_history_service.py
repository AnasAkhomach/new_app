"""Service layer for managing patient medical histories in the surgical scheduling system."""

from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from models import PatientMedicalHistory


class PatientMedicalHistoryService:
    """Provides services for managing patient medical histories."""

    @staticmethod
    def create_medical_history(db, history_data):
        """Creates a new patient medical history record."""
        try:
            new_history = PatientMedicalHistory(
                patient_id=history_data["patient_id"],
                medical_condition=history_data["medical_condition"],
                diagnosis_date=(
                    history_data["diagnosis_date"]
                    if isinstance(history_data["diagnosis_date"], date)
                    else date.fromisoformat(history_data["diagnosis_date"])
                ),
            )
            db.add(new_history)
            db.commit()
            db.refresh(new_history)
            print(f"Patient medical history {new_history.id} created successfully.")
            return new_history.id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating patient medical history: {e}")
            return None

    @staticmethod
    def get_patient_medical_history(db, history_id):
        """Retrieves a patient medical history record by id and returns a PatientMedicalHistory instance."""
        try:
            history = db.query(PatientMedicalHistory).filter_by(id=history_id).first()
            if history:
                return history
            print(f"No patient medical history found with ID {history_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error retrieving patient medical history: {e}")
            return None

    @staticmethod
    def update_patient_medical_history(db, history_id, update_fields):
        """Updates an existing patient medical history record."""
        try:
            result = (
                db.query(PatientMedicalHistory)
                .filter_by(id=history_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Patient medical history {history_id} updated successfully.")
                return True
            print(
                f"No patient medical history found with ID {history_id} or no new data to update."
            )
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating patient medical history: {e}")
            return False

    @staticmethod
    def delete_patient_medical_history(db, history_id):
        """Deletes a patient medical history record."""
        try:
            result = db.query(PatientMedicalHistory).filter_by(id=history_id).delete()
            db.commit()
            if result:
                print(f"Patient medical history {history_id} deleted successfully.")
                return True
            print(f"No patient medical history found with ID {history_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting patient medical history: {e}")
            return False
