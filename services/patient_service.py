import sys
import os
from pymongo.errors import PyMongoError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import Patient

class PatientService:
    @staticmethod
    def create_patient(patient_data):
        """Creates a new patient record."""
        try:
            document = patient_data.to_document()
            db.patients.insert_one(document)
            print(f"Patient {document['name']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating patient: {e}")

    @staticmethod
    def update_patient(patient_id, update_fields):
        """Updates an existing patient record."""
        try:
            result = db.patients.update_one({"patient_id": patient_id}, {"$set": update_fields})
            if result.modified_count:
                print(f"Patient {patient_id} updated successfully.")
            else:
                print(f"No patient found with ID {patient_id} or no new data to update.")
        except PyMongoError as e:
            print(f"Error updating patient: {e}")

    @staticmethod
    def delete_patient(patient_id):
        """Deletes a patient record."""
        try:
            result = db.patients.delete_one({"patient_id": patient_id})
            if result.deleted_count:
                print(f"Patient {patient_id} deleted successfully.")
            else:
                print(f"No patient found with ID {patient_id}.")
        except PyMongoError as e:
            print(f"Error deleting patient: {e}")

    @staticmethod
    def get_patient(patient_id):
        """Retrieves a patient record by patient_id and returns a Patient instance."""
        try:
            document = db.patients.find_one({"patient_id": patient_id})
            if document:
                return Patient.from_document(document)
            else:
                print(f"No patient found with ID {patient_id}")
                return None
        except PyMongoError as e:
            print(f"Error retrieving patient: {e}")
            return None

# Example usage
if __name__ == "__main__":
    try:
        new_patient = Patient("PAT001", "Alice Johnson", "1985-04-12", "555-1234", "No known allergies", True)
        PatientService.create_patient(new_patient)
    except Exception as e:
        print(f"An error occurred: {e}")
