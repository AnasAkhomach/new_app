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
                logger.debug(
                    f"Equipment '{equipment_name}' used by in-memory surgery {assignment_surgery_id} "
                    f"({assigned_start_dt.isoformat()}-{assigned_end_dt.isoformat()}) "
                    f"during proposed slot ({start_dt.isoformat()}-{end_dt.isoformat()}). Qty: {quantity_needed}"
                )
            # No ValueError expected here for time parsing

        # Check database assignments if DB session is available
        if self.db_session:
            try:
                # Query for SurgeryEquipmentUsage records that overlap with the proposed time
                # and are for the specific equipment_name.
                # This requires joining SurgeryEquipmentUsage -> SurgeryEquipment (for name),
                # and SurgeryEquipmentUsage -> Surgery -> SurgeryRoomAssignment (for times).
                db_usage_query = self.db_session.query(SurgeryEquipmentUsage.quantity)\
                    .join(SurgeryEquipment, SurgeryEquipment.id == SurgeryEquipmentUsage.equipment_id)\
                    .join(Surgery, Surgery.surgery_id == SurgeryEquipmentUsage.surgery_id)\
                    .join(SurgeryRoomAssignment, SurgeryRoomAssignment.surgery_id == Surgery.surgery_id)\
                    .filter(SurgeryEquipment.name == equipment_name)\
                    .filter(SurgeryRoomAssignment.start_time < end_dt)\
                    .filter(SurgeryRoomAssignment.end_time > start_dt)

                if exclude_surgery_id:
                    db_usage_query = db_usage_query.filter(Surgery.surgery_id != exclude_surgery_id)

                overlapping_usages_from_db = db_usage_query.all()

                for usage_qty_tuple in overlapping_usages_from_db:
                    # Assuming usage_qty_tuple is like (quantity,)
                    concurrent_usage_count += usage_qty_tuple[0] if usage_qty_tuple else 0
                    logger.debug(
                        f"Equipment '{equipment_name}' also used by a DB surgery "
                        f"during proposed slot. Adding quantity: {usage_qty_tuple[0] if usage_qty_tuple else 0}"
                    )
            except Exception as e:
                logger.error(f"Error querying database for equipment usage of '{equipment_name}': {e}")
        return concurrent_usage_count

    def is_equipment_available(self, surgery_id, start_time_str, end_time_str, current_schedule_assignments):
        """Checks if required equipment for a surgery is available during the given time slot."""
        try:
            proposed_start_dt = datetime.fromisoformat(start_time_str)
            proposed_end_dt = datetime.fromisoformat(end_time_str)
            if proposed_start_dt >= proposed_end_dt:
                logger.error(f"Invalid time range for equipment check: start time {start_time_str} is not before end time {end_time_str}")
                return False
        except ValueError as e:
            logger.error(f"Invalid time format for equipment availability check: {e}")
            return False

        surgery_obj = next((s for s in self.surgeries_data if str(getattr(s, 'id', getattr(s, 'surgery_id', None))) == str(surgery_id)), None)
        if not surgery_obj:
            logger.warning(f"Equipment Check: Surgery object for ID {surgery_id} not found. Cannot determine required equipment.")
            return False

        required_equipment = self._get_required_equipment_for_surgery(surgery_obj)
        if not required_equipment:
            logger.debug(f"No critical equipment identified as required for surgery {surgery_id}. Assuming equipment available.")
            return True

        for equipment_name, quantity_needed in required_equipment.items():
            if equipment_name not in CRITICAL_EQUIPMENT_INVENTORY:
                logger.debug(f"Equipment '{equipment_name}' required for surgery {surgery_id} is not in critical inventory list. Assuming available.")
                continue # Not a tracked critical equipment

            max_available_count = CRITICAL_EQUIPMENT_INVENTORY[equipment_name]
            if quantity_needed > max_available_count:
                logger.warning(f"Surgery {surgery_id} requires {quantity_needed} units of '{equipment_name}', but only {max_available_count} are available in total inventory.")
                return False

            # Calculate concurrent usage, excluding the current surgery if it's being (re)scheduled
            concurrent_usage = self._calculate_concurrent_equipment_usage(
                equipment_name, proposed_start_dt, proposed_end_dt, current_schedule_assignments, surgery_id
            )
            available_for_this_surgery = max_available_count - concurrent_usage
            if available_for_this_surgery < quantity_needed:
                logger.debug(
                    f"Equipment '{equipment_name}' is not available for surgery {surgery_id}. Required: {quantity_needed}, "
                    f"Max Inventory: {max_available_count}, Concurrent Usage (others): {concurrent_usage}, "
                    f"Effectively Available: {available_for_this_surgery}"
                )
                return False
            logger.debug(
                f"Equipment '{equipment_name}' is available for surgery {surgery_id}. Required: {quantity_needed}, Available for this surgery: {available_for_this_surgery}"
            )
        logger.debug(f"All required critical equipment is available for surgery {surgery_id} from {start_time_str} to {end_time_str}.")
        return True

    def is_feasible(self, schedule_assignments):
        """Checks the overall feasibility of a given schedule (list of assignment dicts/objects)."""
        if not schedule_assignments:
            logger.info("Feasibility Check: Empty schedule is considered feasible.")
            return True

        parsed_assignments_for_check = []
        for i, assign_obj in enumerate(schedule_assignments): # assign_obj is a SurgeryRoomAssignment instance
            try:
                surgery_id_val = assign_obj.surgery_id
                room_id_val = assign_obj.room_id
                start_dt_obj = assign_obj.start_time # Already a datetime object
                end_dt_obj = assign_obj.end_time   # Already a datetime object

                if not all([surgery_id_val, room_id_val, start_dt_obj, end_dt_obj]):
                    logger.warning(f"Feasibility Check: Invalid assignment data at index {i} (missing fields): {assign_obj}")
                    return False

                if not isinstance(start_dt_obj, datetime) or not isinstance(end_dt_obj, datetime):
                    logger.warning(f"Feasibility Check: Invalid datetime types for assignment at index {i}, surgery {surgery_id_val}. Start: {type(start_dt_obj)}, End: {type(end_dt_obj)}")
                    return False

                if start_dt_obj >= end_dt_obj:
                    logger.warning(f"Feasibility Check: Invalid time for surgery {surgery_id_val} in room {room_id_val}: start {start_dt_obj} >= end {end_dt_obj}.")
                    return False

                # Store parsed data (already in correct types) for overlap checks
                parsed_assignments_for_check.append({
                    "surgery_id": surgery_id_val, "room_id": room_id_val,
                    "start_time": start_dt_obj, "end_time": end_dt_obj
                })
            except AttributeError as e: # Catch if assign_obj is not a proper SurgeryRoomAssignment instance
                logger.error(f"Feasibility Check: Error accessing attributes on assignment at index {i}: {assign_obj}. Error: {e}")
                return False
            except Exception as e: # Catch other potential errors
                logger.error(f"Feasibility Check: Unexpected error processing assignment at index {i}: {assign_obj}. Error: {e}")
                return False

        # Check for room overlaps
        room_schedules_map = {}
        for pa_item in parsed_assignments_for_check:
            if pa_item["room_id"] not in room_schedules_map:
                room_schedules_map[pa_item["room_id"]] = []
            room_schedules_map[pa_item["room_id"]].append((pa_item["start_time"], pa_item["end_time"], pa_item["surgery_id"]))

        for room_id_key, assignments_in_room_list in room_schedules_map.items():
            assignments_in_room_list.sort(key=lambda x_item: x_item[0]) # Sort by start time
            for i_idx in range(len(assignments_in_room_list) - 1):
                current_end_time = assignments_in_room_list[i_idx][1]
                next_start_time = assignments_in_room_list[i_idx + 1][0]
                if current_end_time > next_start_time:
                    logger.warning(
                        f"Feasibility Check: Room {room_id_key} overlap: Surgery {assignments_in_room_list[i_idx][2]} ends at {current_end_time} "
                        f"and Surgery {assignments_in_room_list[i_idx + 1][2]} starts at {next_start_time}."
                    )
                    return False

        # Check for surgeon double-booking
        surgeon_schedules_map = {}
        for pa_item in parsed_assignments_for_check:
            surgery_object = next((
                s_obj for s_obj in self.surgeries_data if str(getattr(s_obj, 'id', getattr(s_obj, 'surgery_id', None))) == str(pa_item["surgery_id"])
            ), None)
            if not surgery_object or not hasattr(surgery_object, "surgeon_id") or not surgery_object.surgeon_id:
                logger.debug(
                    f"Feasibility Check: Surgery {pa_item['surgery_id']} has no surgeon_id. Skipping surgeon double-booking check for this assignment."
                )
                continue # Cannot check surgeon if not assigned

            surgeon_id_val = surgery_object.surgeon_id
            if surgeon_id_val not in surgeon_schedules_map:
                surgeon_schedules_map[surgeon_id_val] = []
            surgeon_schedules_map[surgeon_id_val].append((pa_item["start_time"], pa_item["end_time"], pa_item["surgery_id"]))

        for surgeon_id_key, assignments_for_surgeon_list in surgeon_schedules_map.items():
            assignments_for_surgeon_list.sort(key=lambda x_item: x_item[0]) # Sort by start time
            for i_idx in range(len(assignments_for_surgeon_list) - 1):
                current_end_time = assignments_for_surgeon_list[i_idx][1]
                next_start_time = assignments_for_surgeon_list[i_idx + 1][0]
                if current_end_time > next_start_time:
                    logger.warning(
                        f"Feasibility Check: Surgeon {surgeon_id_key} is double-booked: Surgery {assignments_for_surgeon_list[i_idx][2]} ends at {current_end_time} "
                        f"and Surgery {assignments_for_surgeon_list[i_idx + 1][2]} starts at {next_start_time}."
                    )
                    return False

        logger.info("Feasibility Check: Schedule appears feasible based on room and surgeon checks.")
        return True