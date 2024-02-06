import datetime

class OperatingRoom:
    def __init__(self, room_id, location, equipment_list):
        self.room_id = room_id
        self.location = location
        self.equipment_list = equipment_list

    @staticmethod
    def from_document(document):
        """Converts a MongoDB document into an OperatingRoom instance."""
        return OperatingRoom(
            room_id=document.get("room_id"),
            location=document.get("location"),
            equipment_list=document.get("equipment_list", [])
        )

    def to_document(self):
        """Converts the OperatingRoom instance into a dictionary suitable for MongoDB."""
        return {
            "room_id": self.room_id,
            "location": self.location,
            "equipment_list": self.equipment_list
        }


class Patient:
    def __init__(self, patient_id, name, dob, contact_info, medical_history, privacy_consent):
        self.patient_id = patient_id
        self.name = name
        self.dob = dob
        self.contact_info = contact_info
        self.medical_history = medical_history
        self.privacy_consent = privacy_consent

    @staticmethod
    def from_document(document):
        """Converts a MongoDB document into a Patient instance."""
        return Patient(
            patient_id=document.get("patient_id"),
            name=document.get("name"),
            dob=document.get("dob"),
            contact_info=document.get("contact_info"),
            medical_history=document.get("medical_history"),
            privacy_consent=document.get("privacy_consent")
        )

    def to_document(self):
        """Converts instance into a dictionary suitable for MongoDB."""
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "dob": self.dob,
            "contact_info": self.contact_info,
            "medical_history": self.medical_history,
            "privacy_consent": self.privacy_consent
        }


class Staff:
    def __init__(self, staff_id, name, role, contact_info, specialization=None, availability=None):
        self.staff_id = staff_id
        self.name = name
        self.role = role
        self.contact_info = contact_info
        self.specialization = specialization
        self.availability = availability

    @staticmethod
    def from_document(document):
        """Converts a MongoDB document into a Staff instance."""
        return Staff(
            staff_id=document.get("staff_id"),
            name=document.get("name"),
            role=document.get("role"),
            contact_info=document.get("contact_info"),
            specialization=document.get("specialization", None),
            availability=document.get("availability", None)
        )

    def to_document(self):
        """Converts instance into a dictionary suitable for MongoDB."""
        document = {
            "staff_id": self.staff_id,
            "name": self.name,
            "role": self.role,
            "contact_info": self.contact_info,
            "specialization": self.specialization,
            "availability": self.availability
        }
        return document


class Surgeon(Staff):
    def __init__(self, staff_id, name, role, contact_info, specialization, availability):
        super().__init__(staff_id, name, role, contact_info)
        self.specialization = specialization
        self.availability = availability

    def to_document(self):
        document = super().to_document()
        document.update({
            "specialization": self.specialization,
            "availability": self.availability
        })
        return document

class Surgery:
    def __init__(self, surgery_id, patient_id, scheduled_date, surgery_type, urgency_level, duration, status):
        self.surgery_id = surgery_id
        self.patient_id = patient_id
        self.scheduled_date = scheduled_date
        self.surgery_type = surgery_type
        self.urgency_level = urgency_level
        self.duration = duration
        self.status = status

    @staticmethod
    def from_document(document):
        """Creates a Surgery instance from a MongoDB document."""
        return Surgery(
            surgery_id=document.get("surgery_id"),
            patient_id=document.get("patient_id"),
            scheduled_date=document.get("scheduled_date"),
            surgery_type=document.get("surgery_type"),
            urgency_level=document.get("urgency_level"),
            duration=document.get("duration"),
            status=document.get("status")
        )

    def to_document(self):
        """Converts a Surgery instance into a MongoDB document."""
        return {
            "surgery_id": self.surgery_id,
            "patient_id": self.patient_id,
            "scheduled_date": self.scheduled_date,
            "surgery_type": self.surgery_type,
            "urgency_level": self.urgency_level,
            "duration": self.duration,
            "status": self.status
        }

# NOT FINISED YET NEEDS TO Obtain token.json

class SurgeryEquipment:
    def __init__(self, equipment_id, name, type, availability):
        self.equipment_id = equipment_id
        self.name = name
        self.type = type
        self.availability = availability

    @staticmethod
    def from_document(document):
        """Creates a SurgeryEquipment instance from a MongoDB document."""
        return SurgeryEquipment(
            equipment_id=document.get("equipment_id"),
            name=document.get("name"),
            type=document.get("type"),
            availability=document.get("availability"),
        )

    def to_document(self):
        """Converts a SurgeryEquipment instance into a MongoDB document."""
        return {
            "equipment_id": self.equipment_id,
            "name": self.name,
            "type": self.type,
            "availability": self.availability,
        }

class SurgeryEquipmentUsage:
    def __init__(self, usage_id, surgery_id, equipment_id):
        self.usage_id = usage_id
        self.surgery_id = surgery_id
        self.equipment_id = equipment_id

    @staticmethod
    def from_document(document):
        """Creates a SurgeryEquipmentUsage instance from a MongoDB document."""
        return SurgeryEquipmentUsage(
            usage_id=document.get("usage_id"),
            surgery_id=document.get("surgery_id"),
            equipment_id=document.get("equipment_id"),
        )

    def to_document(self):
        """Converts a SurgeryEquipmentUsage instance into a MongoDB document."""
        return {
            "usage_id": self.usage_id,
            "surgery_id": self.surgery_id,
            "equipment_id": self.equipment_id,
        }

class SurgeryRoomAssignment:
    def __init__(self, assignment_id, surgery_id, room_id, start_time, end_time):
        self.assignment_id = assignment_id
        self.surgery_id = surgery_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def from_document(document):
        """Creates a SurgeryRoomAssignment instance from a MongoDB document."""
        return SurgeryRoomAssignment(
            assignment_id=document.get("assignment_id"),
            surgery_id=document.get("surgery_id"),
            room_id=document.get("room_id"),
            start_time=document.get("start_time"),
            end_time=document.get("end_time"),
        )

    def to_document(self):
        """Converts a SurgeryRoomAssignment instance into a MongoDB document."""
        return {
            "assignment_id": self.assignment_id,
            "surgery_id": self.surgery_id,
            "room_id": self.room_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

class StaffAssignment:
    def __init__(self, staff_id, role, assignment_id=None):
        self.assignment_id = assignment_id  # Optional, depending on if you're tracking assignments separately
        self.staff_id = staff_id
        self.role = role

    @staticmethod
    def from_document(document):
        """Converts a MongoDB document to a StaffAssignment instance."""
        return StaffAssignment(
            assignment_id=document.get("assignment_id"),
            staff_id=document.get("staff_id"),
            role=document.get("role")
        )

    def to_document(self):
        """Converts the StaffAssignment instance into a MongoDB document."""
        return {
            "assignment_id": self.assignment_id,
            "staff_id": self.staff_id,
            "role": self.role
        }
    
class SurgeryStaffAssignment:
    def __init__(self, assignment_id, surgery_id, staff_id, role):
        self.assignment_id = assignment_id
        self.surgery_id = surgery_id
        self.staff_id = staff_id
        self.role = role

    def to_document(self):
        """
        Converts the SurgeryStaffAssignment instance into a dictionary suitable for MongoDB.
        This method is crucial for creating and updating MongoDB documents based on the object's current state.
        """
        return {
            "assignment_id": self.assignment_id,
            "surgery_id": self.surgery_id,
            "staff_id": self.staff_id,
            "role": self.role
        }

    @staticmethod
    def from_document(document):
        """
        Static method to create an instance of SurgeryStaffAssignment from a MongoDB document.
        This method facilitates the conversion from database records back into Python objects.
        """
        return SurgeryStaffAssignment(
            assignment_id=document.get("assignment_id"),
            surgery_id=document.get("surgery_id"),
            staff_id=document.get("staff_id"),
            role=document.get("role")
        )

class SurgeryAppointment:
    def __init__(self, appointment_id, surgery_id, patient_id, staff_assignments, room_id, start_time, end_time):
        self.appointment_id = appointment_id
        self.surgery_id = surgery_id
        self.patient_id = patient_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.staff_assignments = [StaffAssignment(**sa) if isinstance(sa, dict) else sa for sa in staff_assignments]


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