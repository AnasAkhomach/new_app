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
        self.start_time = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') if isinstance(start_time, str) else start_time
        
    def to_document(self):
        """Converts the instance into a dictionary suitable for MongoDB."""
        return {
            "assignment_id": self.assignment_id,
            "surgery_id": self.surgery_id,
            "room_id": self.room_id,
            "start_time": self.start_time,
            "end_time": self.end_time
        }

class SurgeryRoomAssignment:
    def __init__(self, assignment_id, surgery_id, room_id, start_time, end_time):
        self.assignment_id = assignment_id
        self.surgery_id = surgery_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
    
    def to_document(self):
        return {
            "assignment_id": self.assignment_id,
            "surgery_id": self.surgery_id,
            "room_id": self.room_id,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


class StaffAssignment:
    def __init__(self, staff_id, role):
        self.staff_id = staff_id
        self.role = role

    def __str__(self):
        return f"{self.role} - {self.staff_id}"

    def to_document(self):
        """Converts the StaffAssignment instance into a dictionary suitable for MongoDB."""
        return {
            "staff_id": self.staff_id,
            "role": self.role
        }

    @staticmethod
    def save(appointment, db):
        document = appointment.to_document()
        db.surgery_appointments.insert_one(document)

class SurgeryAppointment:
    def __init__(self, appointment_id, surgery_id, patient_id, staff_assignments, room_id, start_time, end_time):
        self.appointment_id = appointment_id
        self.surgery_id = surgery_id
        self.patient_id = patient_id
        self.staff_assignments = [StaffAssignment(**sa) for sa in staff_assignments]  # Convert dicts to StaffAssignment objects
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def from_document(document):
        staff_assignments = [StaffAssignment(sa["staff_id"], sa["role"]) for sa in document["staff_assignments"]]
        return SurgeryAppointment(
            document["appointment_id"],
            document["surgery_id"],
            document["patient_id"],
            staff_assignments,
            document["room_id"],
            document["start_time"],
            document["end_time"]
        )
 
    def to_document(self):
        """Converts the SurgeryAppointment instance into a dictionary suitable for MongoDB."""
        return {
            "appointment_id": self.appointment_id,
            "surgery_id": self.surgery_id,
            "patient_id": self.patient_id,
            "staff_assignments": [{"staff_id": sa.staff_id, "role": sa.role} for sa in self.staff_assignments],
            "room_id": self.room_id,
            "start_time": self.start_time,
            "end_time": self.end_time
        }