from datetime import datetime, time

class Surgery:
    """
    Simple model for a surgery.
    """
    def __init__(self, surgery_id, surgery_type_id, duration_minutes, surgeon_id, urgency_level="Medium"):
        self.surgery_id = surgery_id
        self.surgery_type_id = surgery_type_id
        self.duration_minutes = duration_minutes
        self.surgeon_id = surgeon_id
        self.urgency_level = urgency_level
    
    def __repr__(self):
        return f"Surgery(id={self.surgery_id}, type={self.surgery_type_id}, duration={self.duration_minutes}min, surgeon={self.surgeon_id})"

class OperatingRoom:
    """
    Simple model for an operating room.
    """
    def __init__(self, room_id, operational_start_time=None, name=None):
        self.room_id = room_id
        self.operational_start_time = operational_start_time
        self.name = name or f"Room {room_id}"
    
    def __repr__(self):
        start_time_str = self.operational_start_time.strftime("%H:%M:%S") if self.operational_start_time else "None"
        return f"OperatingRoom(id={self.room_id}, name='{self.name}', start_time={start_time_str})"

class SurgeryRoomAssignment:
    """
    Simple model for a surgery room assignment.
    """
    def __init__(self, surgery_id, room_id, start_time, end_time):
        self.surgery_id = surgery_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
    
    def __repr__(self):
        start_str = self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else "None"
        end_str = self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "None"
        return f"SurgeryRoomAssignment(surgery={self.surgery_id}, room={self.room_id}, {start_str} to {end_str})"

class SurgeryEquipment:
    """
    Simple model for surgery equipment.
    """
    def __init__(self, equipment_id, name, equipment_type, availability=True):
        self.equipment_id = equipment_id
        self.name = name
        self.type = equipment_type
        self.availability = availability
    
    def __repr__(self):
        return f"SurgeryEquipment(id={self.equipment_id}, name='{self.name}', type='{self.type}', available={self.availability})"

class SurgeryEquipmentUsage:
    """
    Simple model for surgery equipment usage.
    """
    def __init__(self, usage_id, surgery_id, equipment_id, usage_start_time=None, usage_end_time=None):
        self.usage_id = usage_id
        self.surgery_id = surgery_id
        self.equipment_id = equipment_id
        self.usage_start_time = usage_start_time
        self.usage_end_time = usage_end_time
    
    def __repr__(self):
        return f"SurgeryEquipmentUsage(id={self.usage_id}, surgery={self.surgery_id}, equipment={self.equipment_id})"
