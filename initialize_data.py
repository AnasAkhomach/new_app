def initialize_patients():
    return [
        {
            "patient_id": "P001",
            "name": "John Doe",
            "dob": "1990-01-01",
            "contact_info": {
                "phone": "555-0100",
                "email": "john.doe@example.com"
            },
            "medical_history": [
                {"condition": "Condition A", "date_diagnosed": "2018-05-01"},
                {"condition": "Condition B", "date_diagnosed": "2019-11-15"},
                # Add more medical history records as needed
            ],
            "privacy_consent": True
        },
        # Add more patient documents as needed...
    ]

def initialize_staff_members():
    return [
        {
            "staff_id": "S001",
            "name": "Jane Smith",
            "role": "Nurse",
            "specialization": None,  # This can be null/None for non-surgeons
            "contact_info": {
                "phone": "555-0101",
                "email": "jane.smith@example.com"
            },
            "availability_schedule": [
                {"day": "Monday", "start": "08:00", "end": "17:00"},
                {"day": "Tuesday", "start": "08:00", "end": "17:00"},
                # Add more availability slots as needed
            ]
        },
        # Add more staff member documents as needed...
    ]

def initialize_surgeons():
    return [
        {
            "staff_id": "S002",
            "name": "Dr. Alex Johnson",
            "specialization": "Cardiology",
            "contact_info": "555-0102",
            "availability": [{"start": "2023-07-01 08:00", "end": "2023-07-01 16:00"}]
        },
        # Add more surgeon documents as needed...
    ]

def initialize_operating_rooms():
    return [
        {
            "room_id": "OR001",
            "location": "Main Building - Room 101",
            "equipment_list": []
        },
        # Add more operating room documents as needed...
    ]

def initialize_surgeries():
    return [
        {
            "surgery_id": "SUR001",
            "patient_id": "P001",
            "scheduled_date": "2023-07-01",  # Use an actual date
            "estimated_start_time": "08:00",  # New
            "estimated_end_time": "10:00",  # New
            "surgery_type": "Appendectomy",
            "urgency_level": "High",
            "duration": 120,
            "status": "Scheduled",
            "priority": "Normal"
        },
        # Add more surgery documents as needed...
    ]

def initialize_surgery_equipments():
    return [
        {
            "equipment_id": "EQ001",
            "name": "Scalpel",
            "type": "Tool",
            "availability": True
        },
        # Add more surgery equipment documents as needed...
    ]

def initialize_surgery_equipment_usages():
    return [
        {
            "usage_id": "EU001",
            "surgery_id": "SUR001",
            "equipment_id": "EQ001"
        },
        # Add more surgery equipment usage documents as needed...
    ]

def initialize_surgery_room_assignments():
    return [
        {
            "assignment_id": "RA001",
            "surgery_id": "SUR001",
            "room_id": "OR001",
            "start_time": "2023-07-01 08:00",
            "end_time": "2023-07-01 10:00"
        },
        # Add more surgery room assignment documents as needed...
    ]

def initialize_surgery_staff_assignments():
    return [
        {
            "assignment_id": "SA001",
            "surgery_id": "SUR001",
            "staff_id": "S002",
            "role": "Surgeon"
        },
        # Add more surgery staff assignment documents as needed...
    ]

def initialize_surgery_appointments():
    return [
        {
            "appointment_id": "APPT001",
            "surgery_id": "SUR001",
            "patient_id": "P001",
            "staff_assignments": [
                {
                    "staff_id": "S002",
                    "role": "Lead Surgeon"
                }
                # Add more staff assignments as needed
            ],
            "room_id": "OR001",
            "start_time": "2023-07-01T09:00:00",
            "end_time": "2023-07-01T11:00:00"
        },
        # Add more appointments as needed...
    ]
