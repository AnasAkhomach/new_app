# surgery_scheduling_service.py

from datetime import datetime, timedelta
from pymongo.errors import PyMongoError
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import Surgery, Surgeon, OperatingRoom, SurgeryEquipment, SurgeryRoomAssignment, SurgeryEquipmentUsage, SurgeryStaffAssignment, Patient
from scheduling_utils import (is_surgeon_available, is_room_available,
                              is_equipment_available, mongodb_transaction)


class SurgerySchedulingService:
    def __init__(self, db):
        self.db = db

    def is_feasible(self, surgery_id, new_room_id, new_start_time, new_end_time):
        """
        Checks if a proposed surgery schedule is feasible.

        Args:
            surgery_id (str): The ID of the surgery to be scheduled.
            new_room_id (str): The ID of the proposed operating room.
            new_start_time (datetime): The proposed start time of the surgery.
            new_end_time (datetime): The proposed end time of the surgery.

        Returns:
            bool: True if the schedule is feasible, False otherwise.
        """
        # Fetch the surgery, surgeon, and required equipment details
        surgery = self.db.surgeries.find_one({"_id": surgery_id})
        if not surgery:
            print("Surgery not found.")
            return False

        surgeon_id = surgery['surgeon_id']
        equipment_ids = surgery['required_equipment_ids']

        # Check surgeon availability
        if not is_surgeon_available(surgeon_id, new_start_time, new_end_time, self.db):
            print(f"Surgeon {surgeon_id} is not available.")
            return False

        # Check operating room availability
        if not is_room_available(new_room_id, new_start_time, new_end_time, self.db):
            print(f"Room {new_room_id} is not available.")
            return False

        # Check equipment availability
        for equipment_id in equipment_ids:
            if not is_equipment_available(equipment_id, new_start_time, new_end_time, self.db):
                print(f"Equipment {equipment_id} is not available.")
                return False

        return True

    def schedule_surgery(self, surgery_data):
        """Attempt to schedule a surgery and save it to the database.

        Args:
            surgery_data (dict): Information about the surgery to be scheduled.

        Returns:
            bool: True if surgery was scheduled successfully, False otherwise.
        """
        try:
                        # Create instances from surgery_data
            surgery = Surgery(
                surgery_id=surgery_data['surgery_id'],
                patient_id=surgery_data['patient_id'],
                surgeon_id=surgery_data['surgeon_id'],
                room_id=surgery_data['room_id'],
                scheduled_date=surgery_data['scheduled_date'],
                surgery_type=surgery_data['surgery_type'],
                urgency_level=surgery_data['urgency_level'],
                duration=surgery_data['duration'],
                status=surgery_data['status'],
                start_time=surgery_data['start_time'],
                end_time=surgery_data['end_time'],
                required_equipment_ids=surgery_data.get('required_equipment_ids', [])
            )
            
            # Create instances from surgery_data
            surgery = Surgery(**surgery_data)
            surgeon = self.db.surgeons.find_one({"_id": surgery.surgeon_id})
            equipment_list = [self.db.equipment.find_one({"_id": equipment_id}) for equipment_id in surgery.required_equipment_ids]
            room = self.db.operating_rooms.find_one({"_id": surgery.room_id})

            # Convert strings to datetime if necessary
            proposed_start = datetime.strptime(surgery.start_time, "%Y-%m-%dT%H:%M:%S")
            proposed_end = proposed_start + timedelta(minutes=surgery.duration)

            # Check availability using the functions from scheduling_utils
            surgeon_id = surgery_data['surgeon_id'] 
            if not is_surgeon_available(surgeon_id, proposed_start, proposed_end, self.db):
                print(f"Surgeon with ID {surgeon_id} is not available.")
                return False

            surgeon = self.db.surgeons.find_one({"_id": surgery_data['surgeon_id']})
            if surgeon is None:
                print(f"Surgeon with ID {surgery_data['surgeon_id']} not found.")
                return False

            surgeon_id = surgeon['_id']  # Proceed now that we have confirmed surgeon is not None
            if not is_surgeon_available(surgeon_id, proposed_start, proposed_end, self.db):
                print(f"Surgeon with ID {surgeon_id} is not available.")
                return False

            if not is_room_available(room, proposed_start, proposed_end, self.db):
                print(f"Room with ID {surgery.room_id} is not available.")
                return False

            # Assuming Surgery model has a method to check equipment availability
            if any(equipment['availability'] == False for equipment in equipment_list):
                print("One or more required pieces of equipment are not available.")
                return False
            
            # Assuming surgery_data includes patient details
            patient_id = surgery_data['patient_id']
            patient = self.db.patients.find_one({"_id": patient_id})

            if not patient:
                # Patient does not exist, create a new patient record
                new_patient = Patient(
                    patient_id=patient_id,  # Generate or use the provided ID
                    name=surgery_data['patient_name'],
                    dob=surgery_data['patient_dob'],
                    contact_info=surgery_data['patient_contact_info'],
                    medical_history=surgery_data['patient_medical_history'],
                    privacy_consent=surgery_data['patient_privacy_consent']
                )
                self.db.patients.insert_one(new_patient.to_document(), session=session)
                print(f"New patient created with ID {patient_id}.")
            else:
                print(f"Patient with ID {patient_id} already exists.")

            # Everything is available, proceed with scheduling
            with mongodb_transaction(self.db) as session:
                
                proposed_end_iso = proposed_end.isoformat() if isinstance(proposed_end, datetime) else proposed_end
                # Insert the surgery into the database
                self.db.surgeries.insert_one(surgery.to_document(), session=session)
                # Create a room assignment for the surgery
                room_assignment = SurgeryRoomAssignment(
                    assignment_id=surgery.surgery_id,  # Using surgery_id as assignment_id for simplicity
                    surgery_id=surgery.surgery_id,
                    room_id=surgery.room_id,
                    start_time=surgery.start_time,  # Assuming surgery.start_time is in the correct format
                    end_time=proposed_end_iso  # Use the ISO formatted end time
                )
                self.db.surgery_room_assignments.insert_one(room_assignment.to_document(), session=session)
                # Create equipment usage entries for the surgery
                for equipment_id in surgery.required_equipment_ids:
                    equipment_usage = SurgeryEquipmentUsage(
                        usage_id=surgery.surgery_id,  # Using surgery_id as usage_id for simplicity
                        surgery_id=surgery.surgery_id,
                        equipment_id=equipment_id
                    )
                    self.db.surgery_equipment_usage.insert_one(equipment_usage.to_document(), session=session)
                
                for surgeon_info in surgery_data['surgeons']:  # Assuming surgery_data includes surgeon details
                    surgeon_assignment = SurgeryStaffAssignment(
                        assignment_id=...,
                        surgery_id=surgery.surgery_id,
                        surgeon_id=surgeon_info['surgeon_id'],
                        role=surgeon_info['role']
                    )
                    self.db.surgery_surgeon_assignments.insert_one(surgeon_assignment.to_document(), session=session)

                print(f"Surgery with ID {surgery.surgery_id} scheduled successfully.")
                return True
        except (PyMongoError, ValueError) as e:
            print(f"Failed to schedule surgery due to an error: {e}")
            return False

# Example usage
if __name__ == "__main__":
    db = db  # Your database instance from db_config
    scheduling_service = SurgerySchedulingService(db)
    surgery_data = {
        "surgery_id": "Surgery123",
        "patient_id": "Patient123",
        "surgeon_id": "Surgeon123",
        "room_id": "Room123",
        "scheduled_date": "2024-02-07",
        "surgery_type": "Type123",
        "urgency_level": "High",
        "duration": 120,
        "status": "Scheduled",
        "start_time": "2024-02-07T09:00:00",
        "end_time": "2024-02-07T11:00:00",
        "required_equipment_ids": ["Equipment1", "Equipment2"]  # Example
    }
    result = scheduling_service.schedule_surgery(surgery_data)
    print("Surgery scheduled:", result)