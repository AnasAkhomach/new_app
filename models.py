import datetime

class OperatingRoom:
    def __init__(self, room_id, location, equipment_list):
        self.room_id = room_id
        self.location = location
        self.equipment_list = equipment_list  # List of SurgeryEquipment objects

class Patient:
    def __init__(self, patient_id, name, dob, contact_info, medical_history, privacy_consent):
        self.patient_id = patient_id
        self.name = name
        self.dob = datetime.datetime.strptime(dob, '%Y-%m-%d') if isinstance(dob, str) else dob
        self.contact_info = contact_info
        self.medical_history = medical_history
        self.privacy_consent = privacy_consent

class Staff:
    def __init__(self, staff_id, name, role, contact_info):
        self.staff_id = staff_id
        self.name = name
        self.role = role
        self.contact_info = contact_info

class Surgeon(Staff):
    def __init__(self, staff_id, name, specialization, contact_info, availability):
        super().__init__(staff_id, name, 'Surgeon', contact_info)
        self.specialization = specialization  # Can be a list or a single string
        self.availability = availability  # List of tuples with available times (start, end)

    def has_expertise_for(self, surgery_type):
        return surgery_type in self.specialization if isinstance(self.specialization, list) else surgery_type == self.specialization

    def is_available(self, scheduled_time):
        for start, end in self.availability:
            if start <= scheduled_time <= end:
                return True
        return False

class Surgery:
    def __init__(self, surgery_id, patient_id, scheduled_date, surgery_type, urgency_level, duration, status):
        self.surgery_id = surgery_id
        self.patient_id = patient_id
        self.scheduled_date = datetime.datetime.strptime(scheduled_date, '%Y-%m-%d %H:%M') if isinstance(scheduled_date, str) else scheduled_date
        self.surgery_type = surgery_type
        self.urgency_level = urgency_level
        self.duration = duration
        self.status = status

class SurgeryEquipment:
    def __init__(self, equipment_id, name, type, availability):
        self.equipment_id = equipment_id
        self.name = name
        self.type = type
        self.availability = availability

class SurgeryEquipmentUsage:
    def __init__(self, usage_id, surgery_id, equipment_id):
        self.usage_id = usage_id
        self.surgery_id = surgery_id
        self.equipment_id = equipment_id

class SurgeryRoomAssignment:
    def __init__(self, assignment_id, surgery_id, room_id, start_time, end_time):
        self.assignment_id = assignment_id
        self.surgery_id = surgery_id
        self.room_id = room_id
        self.start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M') if isinstance(start_time, str) else start_time
        self.end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M') if isinstance(end_time, str) else end_time

class SurgeryStaffAssignment:
    def __init__(self, assignment_id, surgery_id, staff_id, role):
        self.assignment_id = assignment_id
        self.surgery_id = surgery_id
        self.staff_id = staff_id
        self.role = role
