# patient_service.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import Patient


class PatientService:
    @staticmethod
    def create_patient(patient_data):
        """Creates a new patient record."""
        document = patient_data.to_document()
        db.patients.insert_one(document)
        print(f"Patient {document['name']} created successfully.")

    @staticmethod
    def update_patient(patient_id, update_fields):
        """Updates an existing patient record."""
        db.patients.update_one({"patient_id": patient_id}, {"$set": update_fields})
        print(f"Patient {patient_id} updated successfully.")

    @staticmethod
    def delete_patient(patient_id):
        """Deletes a patient record."""
        db.patients.delete_one({"patient_id": patient_id})
        print(f"Patient {patient_id} deleted successfully.")

# Example usage
if __name__ == "__main__":
    new_patient = Patient("PAT001", "Alice Johnson", "1985-04-12", "555-1234", "No known allergies", True)
    PatientService.create_patient(new_patient)
