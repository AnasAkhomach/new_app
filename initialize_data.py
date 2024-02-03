# initialize_data.py
from models import OperatingRoom, Patient, Staff, Surgeon, Surgery, SurgeryEquipment, SurgeryEquipmentUsage, SurgeryRoomAssignment, SurgeryStaffAssignment

def initialize_patients():
    return [
        Patient(patient_id="P001", name="John Doe", dob="1990-01-01", 
                contact_info="555-0100", medical_history="None", privacy_consent=True),
        # Add more patients as needed...
    ]

def initialize_staff_members():
    return [
        Staff(staff_id="S001", name="Jane Smith", role="Nurse", 
              contact_info="555-0101"),
        # Add more staff members as needed...
    ]

def initialize_surgeons():
    return [
        Surgeon(staff_id="S002", name="Dr. Alex Johnson", specialization="Cardiology", 
                contact_info="555-0102", availability=[("2023-07-01 08:00", "2023-07-01 16:00")]),
        # Add more surgeons as needed...
    ]

def initialize_operating_rooms():
    return [
        OperatingRoom(room_id="OR001", location="Main Building - Room 101", equipment_list=[]),
        # Add more operating rooms as needed...
    ]

def initialize_surgeries():
    return [
        Surgery(surgery_id="SUR001", patient_id="P001", scheduled_date=None, 
                surgery_type="Appendectomy", urgency_level="High", duration=120, status="Scheduled"),
        # Add more surgeries as needed...
    ]

def initialize_surgery_equipments():
    return [
        SurgeryEquipment(equipment_id="EQ001", name="Scalpel", type="Tool", availability=True),
        # Add more surgery equipment as needed...
    ]

def initialize_surgery_equipment_usages():
    return [
        SurgeryEquipmentUsage(usage_id="EU001", surgery_id="SUR001", equipment_id="EQ001"),
        # Add more surgery equipment usages as needed...
    ]

def initialize_surgery_room_assignments():
    return [
        SurgeryRoomAssignment(assignment_id="RA001", surgery_id="SUR001", room_id="OR001", 
                              start_time="2023-07-01 08:00", end_time="2023-07-01 10:00"),
        # Add more surgery room assignments as needed...
    ]

def initialize_surgery_staff_assignments():
    return [
        SurgeryStaffAssignment(assignment_id="SA001", surgery_id="SUR001", staff_id="S002", role="Surgeon"),
        # Add more surgery staff assignments as needed...
    ]
