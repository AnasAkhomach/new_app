# This file will contain the logic for checking schedule feasibility.
import logging
from datetime import datetime, timedelta
import json # For parsing equipment requirements if stored as JSON string
from models import Surgery, SurgeryRoomAssignment, SurgeryEquipment, SurgeryEquipmentUsage # Assuming models.py is accessible

logger = logging.getLogger(__name__)

# Define critical equipment inventory at the module level or pass it to the class
CRITICAL_EQUIPMENT_INVENTORY = {
    "Da Vinci Robotic System": 1,
    "Intraoperative MRI": 1,
    "Advanced Navigation System": 2,
    "Specialized Cardiac Bypass Machine": 2,
    "Neurosurgical Navigation System": 1,
    "Specialized Orthopedic Drill Set": 3,
    "Specialized Laparoscopic Equipment": 4,
    "Specialized Ophthalmic Microscope": 2,
}

class FeasibilityChecker:
    def __init__(self, db_session, surgeries_data, operating_rooms_data, all_surgery_equipments_data):
        self.db_session = db_session
        self.surgeries_data = surgeries_data # Full list of Surgery objects/data
        self.operating_rooms_data = operating_rooms_data # Full list of OR objects/data
        self.all_surgery_equipments_data = all_surgery_equipments_data # Full list of SurgeryEquipment objects/data
        logger.info("FeasibilityChecker initialized.")

    def is_surgeon_available(
        self,
        surgeon_id,
        start_time_str,
        end_time_str,
        current_schedule_assignments, # Pass current assignments for this check
        current_surgery_id_to_ignore=None,
    ):
        """Checks if a surgeon is available during the given time slot, optionally ignoring a specific surgery."""
        try:
            proposed_start_dt = datetime.fromisoformat(start_time_str)
            proposed_end_dt = datetime.fromisoformat(end_time_str)
        except ValueError as e:
            logger.error("Invalid time format for surgeon availability check: %s", e)
            return False

        for assignment_obj in current_schedule_assignments: # assignment_obj is a SurgeryRoomAssignment instance
            assignment_surgery_id = assignment_obj.surgery_id
            assigned_start_dt = assignment_obj.start_time # This is now a datetime object
            assigned_end_dt = assignment_obj.end_time   # This is now a datetime object

            if not all([assignment_surgery_id, assigned_start_dt, assigned_end_dt]):
                logger.warning(f"Skipping malformed in-memory assignment (missing data): {assignment_obj}")
                continue

            if not isinstance(assigned_start_dt, datetime) or not isinstance(assigned_end_dt, datetime):
                logger.warning(f"Skipping in-memory assignment for surgery {assignment_surgery_id} due to invalid datetime types: start={type(assigned_start_dt)}, end={type(assigned_end_dt)}")
                continue

            if (
                current_surgery_id_to_ignore
                and str(assignment_surgery_id) == str(current_surgery_id_to_ignore)
            ):
                logger.debug(
                    "Ignoring surgery %s for surgeon %s availability check (currently being modified).",
                    current_surgery_id_to_ignore,
                    surgeon_id,
                )
                continue

            # Find the surgery details from self.surgeries_data using assignment_surgery_id
            surgery_details = next((
                s for s in self.surgeries_data if str(getattr(s, 'id', getattr(s, 'surgery_id', None))) == str(assignment_surgery_id)
            ), None)

            if surgery_details and str(getattr(surgery_details, "surgeon_id", None)) == str(surgeon_id):
                # assigned_start_dt and assigned_end_dt are already datetime objects
                if (
                    proposed_start_dt < assigned_end_dt
                    and assigned_start_dt < proposed_end_dt
                ):
                    logger.debug(
                        "Surgeon %s is busy with in-memory surgery %s (%s-%s) during proposed slot (%s-%s).",
                        surgeon_id,
                        assignment_surgery_id,
                        assigned_start_dt.isoformat(),
                        assigned_end_dt.isoformat(),
                        proposed_start_dt.isoformat(),
                        proposed_end_dt.isoformat(),
                    )
                    return False
            # No ValueError expected here for time parsing as they are already datetime objects

        if self.db_session:
            try:
                overlapping_db_query = (
                    self.db_session.query(SurgeryRoomAssignment)
                    .join(Surgery, Surgery.surgery_id == SurgeryRoomAssignment.surgery_id)
                    .filter(Surgery.surgeon_id == surgeon_id)
                    .filter(
                        SurgeryRoomAssignment.start_time < proposed_end_dt,
                        SurgeryRoomAssignment.end_time > proposed_start_dt,
                    )
                )
                if current_surgery_id_to_ignore:
                    overlapping_db_query = overlapping_db_query.filter(
                        SurgeryRoomAssignment.surgery_id != current_surgery_id_to_ignore
                    )
                db_conflicts = overlapping_db_query.all()
                if db_conflicts:
                    logger.debug(
                        "Surgeon %s is busy with existing DB assignments during proposed slot %s - %s.",
                        surgeon_id, proposed_start_dt.isoformat(), proposed_end_dt.isoformat()
                    )
                    for db_assign in db_conflicts:
                        logger.debug(
                            "  - Overlapping DB assignment: Surgery %s, Room %s, Time %s-%s",
                            db_assign.surgery_id,
                            db_assign.room_id,
                            db_assign.start_time.isoformat() if isinstance(db_assign.start_time, datetime) else db_assign.start_time,
                            db_assign.end_time.isoformat() if isinstance(db_assign.end_time, datetime) else db_assign.end_time,
                        )
                    return False
            except Exception as e:
                logger.error("Error querying DB for surgeon %s availability: %s", surgeon_id, e)
                return False # Safer to assume unavailable

        logger.debug("Surgeon %s is available for %s to %s.", surgeon_id, start_time_str, end_time_str)
        return True

    def _get_required_equipment_for_surgery(self, surgery_obj):
        """Determines what equipment is required for a given surgery."""
        required_equipment = {}
        surgery_type = getattr(surgery_obj, "surgery_type", "Unknown")

        if surgery_type == "Robotic Prostatectomy":
            required_equipment["Da Vinci Robotic System"] = 1
            required_equipment["Specialized Laparoscopic Equipment"] = 1
        elif surgery_type == "Complex Brain Tumor Resection":
            required_equipment["Intraoperative MRI"] = 1
            required_equipment["Advanced Navigation System"] = 1
            required_equipment["Neurosurgical Navigation System"] = 1
        elif surgery_type == "Cardiac Bypass":
            required_equipment["Specialized Cardiac Bypass Machine"] = 1
        elif surgery_type == "Joint Replacement":
            required_equipment["Specialized Orthopedic Drill Set"] = 1
        elif surgery_type == "Cataract Surgery":
            required_equipment["Specialized Ophthalmic Microscope"] = 1
        elif surgery_type == "Laparoscopic Cholecystectomy":
            required_equipment["Specialized Laparoscopic Equipment"] = 1

        if hasattr(surgery_obj, "is_minimally_invasive") and surgery_obj.is_minimally_invasive:
            required_equipment["Specialized Laparoscopic Equipment"] = (
                required_equipment.get("Specialized Laparoscopic Equipment", 0) + 1
            )

        if hasattr(surgery_obj, "required_equipment") and surgery_obj.required_equipment:
            try:
                if isinstance(surgery_obj.required_equipment, dict):
                    return surgery_obj.required_equipment # Overwrites previous logic if present
                elif isinstance(surgery_obj.required_equipment, str):
                    return json.loads(surgery_obj.required_equipment) # Overwrites
            except Exception as e:
                logger.error(
                    f"Error parsing required_equipment JSON for surgery {getattr(surgery_obj, 'id', 'N/A')}: {e}"
                )
        return required_equipment

    def _calculate_concurrent_equipment_usage(
        self, equipment_name, start_dt, end_dt, current_schedule_assignments, exclude_surgery_id=None
    ):
        """Calculates how many units of a specific equipment are in use during a given time slot."""
        concurrent_usage_count = 0
        # Check in-memory assignments
        for assignment_obj in current_schedule_assignments: # assignment_obj is a SurgeryRoomAssignment instance
            assignment_surgery_id = assignment_obj.surgery_id
            assigned_start_dt = assignment_obj.start_time # This is now a datetime object
            assigned_end_dt = assignment_obj.end_time   # This is now a datetime object

            if not all([assignment_surgery_id, assigned_start_dt, assigned_end_dt]):
                logger.warning(f"Skipping malformed in-memory assignment (missing data) for equipment check: {assignment_obj}")
                continue

            if not isinstance(assigned_start_dt, datetime) or not isinstance(assigned_end_dt, datetime):
                logger.warning(f"Skipping in-memory assignment for surgery {assignment_surgery_id} during equipment check due to invalid datetime types: start={type(assigned_start_dt)}, end={type(assigned_end_dt)}")
                continue

            if exclude_surgery_id and str(assignment_surgery_id) == str(exclude_surgery_id):
                continue

            # Find the surgery details from self.surgeries_data using assignment_surgery_id
            assigned_surgery_details = next((
                s for s in self.surgeries_data if str(getattr(s, 'id', getattr(s, 'surgery_id', None))) == str(assignment_surgery_id)
            ), None)
            if not assigned_surgery_details: continue

            assigned_required_equipment = self._get_required_equipment_for_surgery(assigned_surgery_details)
            if equipment_name not in assigned_required_equipment: continue

            # assigned_start_dt and assigned_end_dt are already datetime objects
            if start_dt < assigned_end_dt and assigned_start_dt < end_dt: # Overlap condition
                quantity_needed = assigned_required_equipment[equipment_name]
                concurrent_usage_count += quantity_needed

        # Check DB assignments if db_session is available
        if self.db_session:
            try:
                # Query for SurgeryRoomAssignments that overlap with the proposed time
                # and require the specific equipment.
                # This requires joining SurgeryRoomAssignment with Surgery (to get surgery_type or required_equipment field)
                # and potentially a SurgeryEquipmentLink table if equipment is explicitly linked.
                # For simplicity, assuming surgery_obj passed to _get_required_equipment_for_surgery has enough info.

                # This is a simplified DB check. A more robust check would involve:
                # 1. Finding all surgeries in DB overlapping the time slot.
                # 2. For each, determine its required equipment.
                # 3. Sum up the usage for 'equipment_name'.
                # The current self.all_surgery_equipments_data might not be directly usable here without knowing which surgery it belongs to in a schedule.
                # Let's refine this to query SurgeryRoomAssignment and then get surgery details.

                overlapping_db_assignments = (
                    self.db_session.query(SurgeryRoomAssignment)
                    .filter(
                        SurgeryRoomAssignment.start_time < end_dt,
                        SurgeryRoomAssignment.end_time > start_dt,
                    )
                )
                if exclude_surgery_id:
                    overlapping_db_assignments = overlapping_db_assignments.filter(
                        SurgeryRoomAssignment.surgery_id != exclude_surgery_id
                    )

                for db_assignment in overlapping_db_assignments.all():
                    db_surgery_details = next((
                        s for s in self.surgeries_data if str(getattr(s, 'id', getattr(s, 'surgery_id', None))) == str(db_assignment.surgery_id)
                    ), None)
                    if not db_surgery_details: continue

                    db_required_equipment = self._get_required_equipment_for_surgery(db_surgery_details)
                    if equipment_name in db_required_equipment:
                        concurrent_usage_count += db_required_equipment[equipment_name]

            except Exception as e:
                logger.error(f"Error querying DB for equipment {equipment_name} usage: {e}")
                # Decide how to handle: assume worst case (max usage) or log and continue?
                # For now, let's assume it contributes to usage to be safe, or return a high number.
                return float('inf') # Indicates an error and likely unavailability

        return concurrent_usage_count

    def is_equipment_available(
        self, surgery_obj, start_time_str, end_time_str, current_schedule_assignments, current_surgery_id_to_ignore=None
    ):
        """Checks if all required equipment for a surgery is available during the given time slot."""
        try:
            proposed_start_dt = datetime.fromisoformat(start_time_str)
            proposed_end_dt = datetime.fromisoformat(end_time_str)
        except ValueError as e:
            logger.error(f"Invalid time format for equipment availability check: {e}")
            return False

        required_equipment_for_proposed_surgery = self._get_required_equipment_for_surgery(surgery_obj)
        if not required_equipment_for_proposed_surgery:
            logger.debug(f"No specific equipment required for surgery {getattr(surgery_obj, 'id', 'N/A')}. Assuming available.")
            return True # No specific equipment needed

        for equip_name, quantity_needed_for_this_surgery in required_equipment_for_proposed_surgery.items():
            if equip_name not in CRITICAL_EQUIPMENT_INVENTORY:
                logger.warning(
                    f"Equipment '{equip_name}' required by surgery {getattr(surgery_obj, 'id', 'N/A')} is not in CRITICAL_EQUIPMENT_INVENTORY. Assuming available if not critical, or issue if it should be listed."
                )
                # Depending on policy, this could be True (if non-critical is assumed available) or False (if all must be tracked)
                # For now, let's assume if it's not in critical inventory, it's a type we don't track scarcity for, or it's an error in data.
                # To be safe, if it's requested, it should be in inventory. Let's flag as unavailable if not in inventory.
                # Update: Let's assume unlisted equipment is infinitely available for now, or handle as per specific project rules.
                # For this implementation, if it's *required* by a surgery, it *must* be in the inventory to check against.
                # If it's not in CRITICAL_EQUIPMENT_INVENTORY, we cannot confirm its availability from this list.
                # This implies a data setup issue or that the equipment is not considered scarce.
                # Let's assume for now that if it's *critical* and *required*, it must be in the inventory.
                # If it's required but not in CRITICAL_EQUIPMENT_INVENTORY, we'll log a warning and assume it's available (non-scarce).
                # This behavior might need refinement based on actual operational rules.
                logger.warning(f"Equipment '{equip_name}' is required but not found in CRITICAL_EQUIPMENT_INVENTORY. Assuming available (non-scarce). Review if this item should be tracked.")
                continue # Move to next required equipment item

            total_inventory_for_equip = CRITICAL_EQUIPMENT_INVENTORY.get(equip_name, 0)
            if total_inventory_for_equip == 0:
                 logger.warning(f"Equipment '{equip_name}' is listed in inventory with 0 units. Effectively unavailable.")
                 return False # No units of this equipment available at all

            # Calculate how many units of this equipment are already in use during the proposed slot
            # Pass current_surgery_id_to_ignore if this check is for modifying an existing surgery's assignment
            concurrent_usage = self._calculate_concurrent_equipment_usage(
                equip_name, proposed_start_dt, proposed_end_dt, current_schedule_assignments, exclude_surgery_id=current_surgery_id_to_ignore
            )

            if concurrent_usage == float('inf'): # Error during DB query for concurrent usage
                logger.error(f"Could not determine concurrent usage for {equip_name} due to DB error. Assuming unavailable.")
                return False

            available_units = total_inventory_for_equip - concurrent_usage
            if available_units < quantity_needed_for_this_surgery:
                logger.debug(
                    f"Equipment '{equip_name}' NOT available for surgery {getattr(surgery_obj, 'id', 'N/A')} during {start_time_str} - {end_time_str}. "
                    f"Required: {quantity_needed_for_this_surgery}, Available: {available_units} (Total: {total_inventory_for_equip}, In Use: {concurrent_usage})"
                )
                return False
            else:
                logger.debug(
                    f"Equipment '{equip_name}' IS available for surgery {getattr(surgery_obj, 'id', 'N/A')}. "
                    f"Required: {quantity_needed_for_this_surgery}, Available: {available_units} (Total: {total_inventory_for_equip}, In Use: {concurrent_usage})"
                )
        logger.debug(f"All required equipment available for surgery {getattr(surgery_obj, 'id', 'N/A')} from {start_time_str} to {end_time_str}.")
        return True

    def is_room_available(
        self, room_id, start_time_str, end_time_str, current_schedule_assignments, current_surgery_id_to_ignore=None
    ):
        """Checks if a specific operating room is available during the given time slot."""
        try:
            proposed_start_dt = datetime.fromisoformat(start_time_str)
            proposed_end_dt = datetime.fromisoformat(end_time_str)
            if proposed_start_dt >= proposed_end_dt:
                logger.error(f"Invalid time range for room availability check: start {start_time_str} not before end {end_time_str}.")
                return False
        except ValueError as e:
            logger.error(f"Invalid time format for room availability check: {e}")
            return False

        # Check in-memory assignments
        for assignment_obj in current_schedule_assignments:
            if str(getattr(assignment_obj, 'room_id', None)) != str(room_id):
                continue # Not in the room we are checking

            assignment_surgery_id = assignment_obj.surgery_id
            assigned_start_dt = assignment_obj.start_time
            assigned_end_dt = assignment_obj.end_time

            if not all([assignment_surgery_id, assigned_start_dt, assigned_end_dt]):
                logger.warning(f"Skipping malformed in-memory assignment for room check: {assignment_obj}")
                continue
            if not isinstance(assigned_start_dt, datetime) or not isinstance(assigned_end_dt, datetime):
                logger.warning(f"Skipping in-memory assignment for surgery {assignment_surgery_id} in room check due to invalid datetime types.")
                continue

            if current_surgery_id_to_ignore and str(assignment_surgery_id) == str(current_surgery_id_to_ignore):
                logger.debug(f"Ignoring surgery {current_surgery_id_to_ignore} for room {room_id} availability check.")
                continue

            # Check for overlap
            if proposed_start_dt < assigned_end_dt and assigned_start_dt < proposed_end_dt:
                logger.debug(
                    f"Room {room_id} is busy with in-memory surgery {assignment_surgery_id} ({assigned_start_dt.isoformat()}-{assigned_end_dt.isoformat()}) "
                    f"during proposed slot ({proposed_start_dt.isoformat()}-{proposed_end_dt.isoformat()})."
                )
                return False

        # Check database assignments if db_session is available
        if self.db_session:
            try:
                overlapping_db_query = (
                    self.db_session.query(SurgeryRoomAssignment)
                    .filter(SurgeryRoomAssignment.room_id == room_id)
                    .filter(
                        SurgeryRoomAssignment.start_time < proposed_end_dt,
                        SurgeryRoomAssignment.end_time > proposed_start_dt,
                    )
                )
                if current_surgery_id_to_ignore:
                    overlapping_db_query = overlapping_db_query.filter(
                        SurgeryRoomAssignment.surgery_id != current_surgery_id_to_ignore
                    )
                db_conflicts = overlapping_db_query.all()
                if db_conflicts:
                    logger.debug(
                        f"Room {room_id} is busy with existing DB assignments during proposed slot {proposed_start_dt.isoformat()} - {proposed_end_dt.isoformat()}."
                    )
                    for db_assign in db_conflicts:
                        logger.debug(
                            f"  - Overlapping DB assignment in Room {room_id}: Surgery {db_assign.surgery_id}, Time {db_assign.start_time.isoformat()}-{db_assign.end_time.isoformat()}"
                        )
                    return False
            except Exception as e:
                logger.error(f"Error querying DB for room {room_id} availability: {e}")
                return False # Safer to assume unavailable

        logger.debug(f"Room {room_id} is available for {start_time_str} to {end_time_str}.")
        return True

    def is_feasible(self, proposed_schedule_assignments, check_db_too=True):
        """Checks the overall feasibility of a given schedule (list of SurgeryRoomAssignment objects)."""
        if not proposed_schedule_assignments:
            logger.info("Feasibility Check: Empty schedule is considered feasible.")
            return True

        # Validate structure and extract key info first to avoid repeated getattr calls
        validated_assignments = []
        for i, assign_obj in enumerate(proposed_schedule_assignments):
            try:
                surgery_id = assign_obj.surgery_id
                surgeon_id = assign_obj.surgeon_id
                room_id = assign_obj.room_id
                start_time_dt = assign_obj.start_time
                end_time_dt = assign_obj.end_time
                surgery_obj = assign_obj.surgery # Assuming this attribute holds the Surgery object or its ID for equipment check

                if not all([surgery_id, surgeon_id, room_id, start_time_dt, end_time_dt, surgery_obj]):
                    logger.warning(f"Feasibility Check: Assignment {i} is missing critical attributes. Schedule infeasible.")
                    return False
                if not isinstance(start_time_dt, datetime) or not isinstance(end_time_dt, datetime):
                    logger.warning(f"Feasibility Check: Assignment {i} (Surgery {surgery_id}) has invalid datetime types. Schedule infeasible.")
                    return False
                if start_time_dt >= end_time_dt:
                    logger.warning(f"Feasibility Check: Assignment {i} (Surgery {surgery_id}) has start time not before end time. Schedule infeasible.")
                    return False

                validated_assignments.append({
                    'original_obj': assign_obj,
                    'surgery_id': str(surgery_id),
                    'surgeon_id': str(surgeon_id),
                    'room_id': str(room_id),
                    'start_time_iso': start_time_dt.isoformat(),
                    'end_time_iso': end_time_dt.isoformat(),
                    'surgery_obj_for_equip': surgery_obj # Pass the surgery object/ID as needed by is_equipment_available
                })
            except AttributeError as e:
                logger.error(f"Feasibility Check: Assignment {i} missing attributes ({e}). Schedule infeasible.")
                return False

        for i, assignment_info in enumerate(validated_assignments):
            surgery_id = assignment_info['surgery_id']
            surgeon_id = assignment_info['surgeon_id']
            room_id = assignment_info['room_id']
            start_time_iso = assignment_info['start_time_iso']
            end_time_iso = assignment_info['end_time_iso']
            surgery_obj_for_equip = assignment_info['surgery_obj_for_equip']

            logger.debug(f"Checking feasibility for assignment {i}: Surgery {surgery_id} in Room {room_id} by Surgeon {surgeon_id} from {start_time_iso} to {end_time_iso}")

            # 1. Check Surgeon Availability
            # Pass the full list of proposed_schedule_assignments for context, ignoring the current one being checked.
            if not self.is_surgeon_available(
                surgeon_id, start_time_iso, end_time_iso, proposed_schedule_assignments, surgery_id_to_ignore=surgery_id, check_db=check_db_too
            ):
                logger.info(f"Feasibility Check: Surgeon {surgeon_id} not available for Surgery {surgery_id}. Schedule infeasible.")
                return False

            # 2. Check Equipment Availability
            # Pass the full list for context, ignoring current surgery.
            if not self.is_equipment_available(
                surgery_obj_for_equip, start_time_iso, end_time_iso, proposed_schedule_assignments, surgery_id_to_ignore=surgery_id, check_db=check_db_too
            ):
                logger.info(f"Feasibility Check: Equipment not available for Surgery {surgery_id}. Schedule infeasible.")
                return False

            # 3. Check Room Availability (already considers DB if session exists)
            # Pass the full list for context, ignoring current surgery.
            if not self.is_room_available(
                room_id, start_time_iso, end_time_iso, proposed_schedule_assignments, current_surgery_id_to_ignore=surgery_id
            ):
                logger.info(f"Feasibility Check: Room {room_id} not available for Surgery {surgery_id}. Schedule infeasible.")
                return False

        logger.info("Feasibility Check: Entire proposed schedule is feasible.")
        return True

    def _get_surgery_duration(self, surgery_id):
        pass