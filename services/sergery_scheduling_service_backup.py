import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from pymongo.errors import PyMongoError

# Assuming db_config.py creates and returns a MongoDB client instance
from  db_config import get_mongo_client, MONGO_URI
from models import Surgery, Surgeon, OperatingRoom, SurgeryEquipment, SurgeryRoomAssignment, SurgeryEquipmentUsage, SurgeryStaffAssignment, Patient
from scheduling_utils import is_surgeon_available, is_room_available, is_equipment_available, mongodb_transaction

#THIS CLASS IST KAPPUT
class SurgerySchedulingServiceUpgraded:
    def __init__(self, db_client):
        self.client = MongoClient(MONGO_URI)
        self.client = db_client  # Store the MongoDB client

    def schedule_surgery(self, surgery_data):
        """Attempt to schedule a surgery and save it to the database."""
        try:
            with mongodb_transaction(self.db) as session:
                surgery = Surgery(**surgery_data)
                surgeon_preferences = self.get_surgeon_preferences(surgery.surgeon_id)

                # Check availability and preferences
                if not self.is_surgery_feasible(surgery, surgeon_preferences):
                    return False

                # Create or update patient record
                self.ensure_patient_exists(surgery.patient_id, surgery_data)

                # Schedule surgery and assign resources
                self.assign_surgery_resources(surgery, session)
                print(f"Surgery with ID {surgery.surgery_id} scheduled successfully.")
                return True
        except (PyMongoError, ValueError) as e:
            print(f"Failed to schedule surgery due to an error: {e}")
            return False

    def is_surgery_feasible(self, surgery, surgeon_preferences):
        """Checks if the surgery scheduling is feasible considering surgeon, room, and equipment availability."""
        proposed_start = datetime.strptime(surgery.start_time, "%Y-%m-%dT%H:%M:%S")
        proposed_end = proposed_start + timedelta(minutes=surgery.duration)
        
        # Simplify checks by encapsulating them in methods (not shown here) that handle the logic.
        return all([
            self.check_surgeon_availability_and_preferences(surgery.surgeon_id, proposed_start, proposed_end, surgeon_preferences),
            is_room_available(surgery.room_id, proposed_start, proposed_end, self.db),
            self.check_equipment_availability(surgery.required_equipment_ids, proposed_start, proposed_end)
        ])

    def get_surgeon_preferences(self, surgeon_id):
        """Retrieve surgeon preferences from the database."""
        surgeon = self.db.surgeons.find_one({"_id": surgeon_id})
        return surgeon.get("preferences", {}) if surgeon else {}

    def ensure_patient_exists(self, patient_id, surgery_data):
        """Ensure the patient record exists, or create a new one."""
        # Check if the patient already exists
        existing_patient = self.db.patients.find_one({"_id": patient_id})
        if not existing_patient:
            # Patient does not exist, so create a new record
            new_patient_data = {
                "_id": patient_id,  # Use patient_id as the document ID
                "name": surgery_data.get('patient_name', 'Unknown'),  # Example field
                "dob": surgery_data.get('patient_dob', '1900-01-01'),  # Example field
                "contact_info": surgery_data.get('patient_contact_info', {}),  # Example field
                "medical_history": surgery_data.get('patient_medical_history', []),  # Example field
                "privacy_consent": surgery_data.get('patient_privacy_consent', False)  # Example field
            }
            self.db.patients.insert_one(new_patient_data)
            print(f"New patient created with ID {patient_id}.")
        else:
            print(f"Patient with ID {patient_id} already exists.")

    def assign_surgery_resources(self, surgery_id, session=None):
        """Assigns necessary resources for a surgery."""
        # Fetch surgery details
        surgery = self.db.surgeries.find_one({"_id": surgery_id}, session=session)
        if not surgery:
            print(f"Surgery with ID {surgery_id} not found.")
            return False

        # Ensure surgeon is available
        surgeon_id = surgery['surgeon_id']
        if not self.is_surgeon_available(surgeon_id, surgery['start_time'], surgery['end_time'], session):
            print(f"Surgeon with ID {surgeon_id} is not available for surgery ID {surgery_id}.")
            return False

        # Ensure operating room is available
        room_id = surgery['room_id']
        if not self.is_room_available(room_id, surgery['start_time'], surgery['end_time'], session):
            print(f"Operating room with ID {room_id} is not available for surgery ID {surgery_id}.")
            return False

        # Check availability of required equipment
        for equipment_id in surgery.get('required_equipment_ids', []):
            if not self.is_equipment_available(equipment_id, surgery['start_time'], surgery['end_time'], session):
                print(f"Required equipment ID {equipment_id} is not available for surgery ID {surgery_id}.")
                return False

        # Assign surgery staff (if this involves more than just the surgeon)
        # This could include anesthesiologists, nurses, etc., if your application tracks these roles
        staff_assignments = surgery.get('staff_assignments', [])
        for staff_assignment in staff_assignments:
            staff_id = staff_assignment['staff_id']
            if not self.is_staff_available(staff_id, surgery['start_time'], surgery['end_time'], session):
                print(f"Staff member with ID {staff_id} is not available for surgery ID {surgery_id}.")
                return False

        # All checks passed, resources are confirmed available
        # Here you would typically write the logic to officially mark these resources as assigned
        # For example, updating the surgery record with confirmed room and equipment assignments
        # Note: This step should also be transaction-safe if you're using sessions

        print(f"All resources assigned successfully for surgery ID {surgery_id}.")
        return True
    
    def close_connection(self):
        """Closes the MongoDB client connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

from pymongo import MongoClient
from sergery_scheduling_service_backup import SurgerySchedulingServiceUpgraded

if __name__ == "__main__":
    mongo_uri = MONGO_URI
    service = SurgerySchedulingServiceUpgraded(MONGO_URI)
    try:
        service = SurgerySchedulingServiceUpgraded(mongo_uri)
        # Your operation logic here...
    finally:
        if service:
            service.close_connection()
