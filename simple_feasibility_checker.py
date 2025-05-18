import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FeasibilityChecker:
    """
    Simple feasibility checker for surgery scheduling.
    """
    
    def __init__(self, db_session, surgeries_data, operating_rooms_data, all_surgery_equipments_data=None):
        """
        Initialize the feasibility checker.
        
        Args:
            db_session: Database session (not used in this simplified version)
            surgeries_data: List of Surgery objects
            operating_rooms_data: List of OperatingRoom objects
            all_surgery_equipments_data: List of equipment data (not used in this simplified version)
        """
        self.db_session = db_session
        self.surgeries_data = {s.surgery_id: s for s in surgeries_data} if surgeries_data else {}
        self.operating_rooms_data = {r.room_id: r for r in operating_rooms_data} if operating_rooms_data else {}
        self.all_surgery_equipments_data = all_surgery_equipments_data
        logger.info("FeasibilityChecker initialized.")
    
    def is_surgeon_available(self, surgeon_id, start_time_str, end_time_str, assignments, current_surgery_id_to_ignore=None):
        """
        Check if a surgeon is available during the given time slot.
        
        Args:
            surgeon_id: ID of the surgeon to check
            start_time_str: Start time of the slot (ISO format string)
            end_time_str: End time of the slot (ISO format string)
            assignments: List of current assignments to check against
            current_surgery_id_to_ignore: ID of a surgery to ignore in the check
            
        Returns:
            True if the surgeon is available, False otherwise
        """
        try:
            proposed_start_dt = datetime.fromisoformat(start_time_str)
            proposed_end_dt = datetime.fromisoformat(end_time_str)
        except ValueError as e:
            logger.error(f"Invalid time format for surgeon availability check: {e}")
            return False
        
        # Check for conflicts with existing assignments
        for assignment in assignments:
            # Skip the assignment we're ignoring
            if current_surgery_id_to_ignore and assignment.surgery_id == current_surgery_id_to_ignore:
                continue
            
            # Get the surgery for this assignment
            surgery_id = assignment.surgery_id
            if surgery_id not in self.surgeries_data:
                continue
            
            surgery = self.surgeries_data[surgery_id]
            
            # Skip if not the same surgeon
            if surgery.surgeon_id != surgeon_id:
                continue
            
            # Check for overlap
            if (proposed_start_dt < assignment.end_time and proposed_end_dt > assignment.start_time):
                logger.debug(f"Surgeon {surgeon_id} is busy with surgery {surgery_id} during proposed slot")
                return False
        
        return True
    
    def is_equipment_available(self, surgery_obj, start_time_str, end_time_str, assignments, current_surgery_id_to_ignore=None):
        """
        Check if equipment is available for a surgery.
        
        In this simplified version, we assume all equipment is available.
        
        Args:
            surgery_obj: Surgery object or ID
            start_time_str: Start time of the slot (ISO format string)
            end_time_str: End time of the slot (ISO format string)
            assignments: List of current assignments to check against
            current_surgery_id_to_ignore: ID of a surgery to ignore in the check
            
        Returns:
            True if equipment is available, False otherwise
        """
        # In this simplified version, we assume all equipment is available
        return True
    
    def is_room_available(self, room_id, start_time_str, end_time_str, assignments, current_surgery_id_to_ignore=None):
        """
        Check if a room is available during the given time slot.
        
        Args:
            room_id: ID of the room to check
            start_time_str: Start time of the slot (ISO format string)
            end_time_str: End time of the slot (ISO format string)
            assignments: List of current assignments to check against
            current_surgery_id_to_ignore: ID of a surgery to ignore in the check
            
        Returns:
            True if the room is available, False otherwise
        """
        try:
            proposed_start_dt = datetime.fromisoformat(start_time_str)
            proposed_end_dt = datetime.fromisoformat(end_time_str)
        except ValueError as e:
            logger.error(f"Invalid time format for room availability check: {e}")
            return False
        
        # Check for conflicts with existing assignments
        for assignment in assignments:
            # Skip the assignment we're ignoring
            if current_surgery_id_to_ignore and assignment.surgery_id == current_surgery_id_to_ignore:
                continue
            
            # Skip if not the same room
            if assignment.room_id != room_id:
                continue
            
            # Check for overlap
            if (proposed_start_dt < assignment.end_time and proposed_end_dt > assignment.start_time):
                logger.debug(f"Room {room_id} is busy during proposed slot")
                return False
        
        return True
    
    def is_feasible(self, surgery_id, room_id, start_time, end_time, current_assignments=None, current_surgery_id_to_ignore=None):
        """
        Check if a surgery assignment is feasible.
        
        Args:
            surgery_id: ID of the surgery to check
            room_id: ID of the room for the assignment
            start_time: Start time of the assignment (ISO format string)
            end_time: End time of the assignment (ISO format string)
            current_assignments: List of current assignments to check against
            current_surgery_id_to_ignore: ID of a surgery to ignore in the check
            
        Returns:
            True if the assignment is feasible, False otherwise
        """
        if current_assignments is None:
            current_assignments = []
        
        # Check if surgery and room exist
        if surgery_id not in self.surgeries_data:
            logger.warning(f"Surgery {surgery_id} not found")
            return False
        
        if room_id not in self.operating_rooms_data:
            logger.warning(f"Room {room_id} not found")
            return False
        
        # Check room availability
        if not self.is_room_available(room_id, start_time, end_time, current_assignments, current_surgery_id_to_ignore):
            return False
        
        # Check surgeon availability
        surgery = self.surgeries_data[surgery_id]
        if not self.is_surgeon_available(surgery.surgeon_id, start_time, end_time, current_assignments, current_surgery_id_to_ignore):
            return False
        
        # Check equipment availability
        if not self.is_equipment_available(surgery, start_time, end_time, current_assignments, current_surgery_id_to_ignore):
            return False
        
        return True
