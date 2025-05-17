"""Service layer for managing patients in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import Patient


class PatientService:
    """Provides services for managing patients."""

    @staticmethod
    def create_patient(db, patient_data):  # Added db parameter
        """Creates a new patient record."""
        try:
            new_patient = Patient(
                name=patient_data["name"],
                dob=patient_data["dob"],
                contact_info=patient_data["contact_info"],
                privacy_consent=patient_data["privacy_consent"],
            )
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)  # Added refresh
            print(f"Patient {new_patient.name} created successfully.")
            return new_patient.patient_id  # Added return ID
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating patient: {e}")
            return None  # Added return None on error

    @staticmethod
    def update_patient(db, patient_id, update_fields):  # Added db parameter
        """Updates an existing patient record."""
        try:
            result = (
                db.query(Patient).filter_by(patient_id=patient_id).update(update_fields)
            )
            db.commit()
            if result:
                print(f"Patient {patient_id} updated successfully.")
                return True
            print(f"No patient found with ID {patient_id} or no new data to update.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating patient: {e}")
            return False

    @staticmethod
    def delete_patient(db, patient_id):  # Added db parameter
        """Deletes a patient record."""
        try:
            result = db.query(Patient).filter_by(patient_id=patient_id).delete()
            db.commit()
            if result:
                print(f"Patient {patient_id} deleted successfully.")
                return True
            print(f"No patient found with ID {patient_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting patient: {e}")
            return False

    @staticmethod
    def get_patient(db, patient_id):  # Added db parameter
        """Retrieves a patient record by patient_id and returns a Patient instance."""
        try:
            patient = db.query(Patient).filter_by(patient_id=patient_id).first()
            if patient:
                return patient
            print(f"No patient found with ID {patient_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error retrieving patient: {e}")
            return None
