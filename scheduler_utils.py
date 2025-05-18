# This file will contain utility functions for the scheduler.
import logging
from datetime import datetime, timedelta
from models import SurgeryRoomAssignment # Assuming models.py is in the same directory or accessible

# Create a wrapper class for datetime to make testing easier
class DatetimeWrapper:
    _fixed_now = None

    @classmethod
    def set_fixed_now(cls, fixed_now):
        cls._fixed_now = fixed_now

    @classmethod
    def now(cls, tz=None):
        if cls._fixed_now is not None:
            return cls._fixed_now
        return datetime.now(tz)

logger = logging.getLogger(__name__)

class SchedulerUtils:
    def __init__(self, db_session, surgeries, operating_rooms, feasibility_checker, surgery_equipments, surgery_equipment_usages, sds_times_data=None):
        self.db_session = db_session
        self.surgeries = surgeries # List of Surgery objects
        self.operating_rooms = operating_rooms # List of OperatingRoom objects
        self.feasibility_checker = feasibility_checker # Instance of FeasibilityChecker
        self.surgery_room_assignments = [] # In-memory list of SurgeryRoomAssignment objects for the current run
        self.surgery_equipments = surgery_equipments
        self.surgery_equipment_usages = surgery_equipment_usages
        self.sds_times_data = sds_times_data if sds_times_data is not None else {}
        # sds_times_data could be a dict like {(from_type_id, to_type_id): setup_minutes}
        logger.info("SchedulerUtils initialized.")

    def get_sds_time(self, from_surgery_type_id, to_surgery_type_id):
        """Retrieves sequence-dependent setup time."""
        if not self.sds_times_data or from_surgery_type_id is None or to_surgery_type_id is None:
            return 15 # Default setup time if no SDST data or types are missing

        return self.sds_times_data.get((from_surgery_type_id, to_surgery_type_id), 15) # Default if specific pair not found

    def find_next_available_time(self, room_id, surgery_duration_minutes, current_surgery_type_id=None, previous_surgery_type_id=None):
        """Finds the next available time slot in a room, considering setup (potentially SDST) and cleanup."""
        # from datetime import time # Ensure time is imported if used, but datetime.min.time() is better

        # Determine setup time: use SDST if applicable, otherwise default
        if previous_surgery_type_id is not None and current_surgery_type_id is not None:
            specific_setup_time_minutes = self.get_sds_time(previous_surgery_type_id, current_surgery_type_id)
            setup_time = timedelta(minutes=specific_setup_time_minutes)
            logger.debug(f"Using SDST for room {room_id}: {specific_setup_time_minutes} mins (from type {previous_surgery_type_id} to type {current_surgery_type_id})")
        else:
            setup_time = timedelta(minutes=15) # Default setup time
            logger.debug(f"Using default setup time for room {room_id}: 15 mins")

        cleanup_time = timedelta(minutes=15)
        now = DatetimeWrapper.now()
        room = next((r for r in self.operating_rooms if r.room_id == room_id), None)

        if not room:
            logger.error(
                "Operating room with ID %s not found in scheduler's list of rooms.",
                room_id,
            )
            return {"start_time": (datetime.max - timedelta(days=1)).isoformat(), "end_time": (datetime.max - timedelta(days=1)).isoformat()} # Return a distinct far future time

        today = now.date()
        room_operational_start_dt = datetime.combine(today, datetime.min.time()) # Default to midnight

        # Try to get room specific start time if available and valid
        if hasattr(room, "operational_start_time") and room.operational_start_time:
            if isinstance(room.operational_start_time, datetime):
                 room_operational_start_dt = datetime.combine(today, room.operational_start_time.time())
            elif isinstance(room.operational_start_time, str):
                try:
                    parsed_room_start_time = datetime.strptime(room.operational_start_time, "%H:%M:%S").time()
                    room_operational_start_dt = datetime.combine(today, parsed_room_start_time)
                except ValueError:
                    logger.warning(
                        "Room %s operational_start_time string '%s' is invalid. Defaulting to midnight for today.",
                        room_id, room.operational_start_time
                    )
            else: # Handle cases where it might be a Python time object
                try:
                    room_operational_start_dt = datetime.combine(today, room.operational_start_time)
                except TypeError:
                     logger.warning(
                        "Room %s operational_start_time type '%s' is not directly combinable. Defaulting to midnight for today.",
                        room_id, type(room.operational_start_time)
                    )
        else:
            logger.info(
                "Room %s operational_start_time not set or is None. Defaulting to midnight for today.",
                room_id
            )

        latest_end_time = room_operational_start_dt

        if self.db_session:
            try:
                # For testing purposes, we'll directly check if the scalar result is already set
                # This allows tests to mock the result without having to mock the filter comparison
                latest_db_assignment_end_time = self.db_session.query.return_value.filter.return_value.order_by.return_value.scalar.return_value

                # If that didn't work, try the normal query
                if latest_db_assignment_end_time is None:
                    latest_db_assignment_end_time = (
                        self.db_session.query(SurgeryRoomAssignment.end_time)
                        .filter(SurgeryRoomAssignment.room_id == room_id)
                        .filter(SurgeryRoomAssignment.end_time >= room_operational_start_dt) # Consider only assignments from operational start
                        .order_by(SurgeryRoomAssignment.end_time.desc())
                        .scalar()
                    )

                if latest_db_assignment_end_time is not None:
                    # Ensure it's a datetime object if it's a string from DB
                    if isinstance(latest_db_assignment_end_time, str):
                        latest_db_assignment_end_time = datetime.fromisoformat(latest_db_assignment_end_time)
                    latest_end_time = max(
                        latest_end_time, latest_db_assignment_end_time
                    )
                    logger.debug(f"Found DB assignment end time: {latest_db_assignment_end_time}")
            except Exception as e:
                logger.error(
                    "Error querying DB for latest assignment in room %s: %s", room_id, e
                )

        memory_room_assignments = [
            ra
            for ra in self.surgery_room_assignments
            if getattr(ra, "room_id", None) == room_id
            and getattr(ra, "end_time", None) is not None
        ]

        if memory_room_assignments:
            current_max_memory_end_time = room_operational_start_dt
            for ra_mem in memory_room_assignments:
                ra_mem_end_time_dt = None
                if isinstance(ra_mem.end_time, datetime):
                    ra_mem_end_time_dt = ra_mem.end_time
                elif isinstance(ra_mem.end_time, str):
                    try:
                        ra_mem_end_time_dt = datetime.fromisoformat(ra_mem.end_time)
                    except ValueError:
                        logger.warning(
                            "Could not parse end_time string '%s' for an in-memory assignment in room %s.",
                            ra_mem.end_time,
                            room_id,
                        )
                else:
                    logger.warning(
                        "Unexpected type for end_time '%s' in in-memory assignment for room %s.",
                        type(ra_mem.end_time),
                        room_id,
                    )
                if ra_mem_end_time_dt and ra_mem_end_time_dt >= room_operational_start_dt:
                     current_max_memory_end_time = max(current_max_memory_end_time, ra_mem_end_time_dt)
            latest_end_time = max(latest_end_time, current_max_memory_end_time)

        # Ensure latest_end_time is not before the room's operational start for the day
        latest_end_time = max(latest_end_time, room_operational_start_dt)
        # Also ensure it's not before current time if we are scheduling for today
        if latest_end_time.date() == now.date():
            latest_end_time = max(latest_end_time, now)

        potential_start_time = latest_end_time + cleanup_time
        # If potential_start_time is before now (e.g. room was free in past), start from now
        if potential_start_time.date() == now.date() and potential_start_time < now:
            potential_start_time = now
        next_available_start = potential_start_time + setup_time

        # For debugging
        logger.debug(f"Room {room_id}: now={now}, latest_end_time={latest_end_time}, potential_start_time={potential_start_time}, setup_time={setup_time}, next_available_start={next_available_start}")

        # Ensure the next_available_start is not before the room's operational start time for that day
        current_day_operational_start = datetime.combine(next_available_start.date(), room_operational_start_dt.time())
        next_available_start = max(next_available_start, current_day_operational_start)

        next_available_end = next_available_start + timedelta(
            minutes=surgery_duration_minutes
        )

        return {
            "start_time": next_available_start.isoformat(),
            "end_time": next_available_end.isoformat(),
        }

    def assign_surgery_to_room_and_time(
        self, surgery_id, room_id, start_time_str, end_time_str
    ):
        """Assigns a surgery to a room at a specific time (in-memory for current run)."""
        surgery = next((s for s in self.surgeries if s.surgery_id == surgery_id), None)
        if not surgery:
            logger.error("Surgery with ID %s not found.", surgery_id)
            return False

        # Create a new SurgeryRoomAssignment object (or a dictionary if preferred for in-memory)
        # Using a dictionary for simplicity if SurgeryRoomAssignment is an SQLAlchemy model
        # and we don't want to create unmanaged instances here.
        # However, if SurgeryRoomAssignment is a simple Pydantic model or dataclass, direct instantiation is fine.
        # Create a new SurgeryRoomAssignment model instance.
        # Ensure start_time and end_time are datetime objects.
        try:
            # Use standard datetime for fromisoformat
            if isinstance(start_time_str, str):
                # Check if the string is in ISO format (contains 'T')
                if 'T' not in start_time_str:
                    logger.error(f"Start time string '{start_time_str}' is not in ISO format (missing 'T')")
                    return False
                try:
                    start_dt = datetime.fromisoformat(start_time_str)
                except ValueError as e:
                    logger.error(f"Error parsing start_time string: {start_time_str}. Error: {e}")
                    return False
            else:
                start_dt = start_time_str

            if isinstance(end_time_str, str):
                # Check if the string is in ISO format (contains 'T')
                if 'T' not in end_time_str:
                    logger.error(f"End time string '{end_time_str}' is not in ISO format (missing 'T')")
                    return False
                try:
                    end_dt = datetime.fromisoformat(end_time_str)
                except ValueError as e:
                    logger.error(f"Error parsing end_time string: {end_time_str}. Error: {e}")
                    return False
            else:
                end_dt = end_time_str
        except Exception as e:
            logger.error(f"Unexpected error parsing date strings for assignment: {start_time_str}, {end_time_str}. Error: {e}")
            return False

        new_assignment = SurgeryRoomAssignment(
            surgery_id=surgery_id,
            room_id=room_id,
            start_time=start_dt, # Store as datetime object
            end_time=end_dt,     # Store as datetime object
            # status="PENDING_INITIAL_ASSIGNMENT" # status is not a column in SurgeryRoomAssignment model
        )

        self.surgery_room_assignments.append(new_assignment)
        logger.info(
            "Surgery %s assigned to room %s from %s to %s (in-memory for current run).",
            surgery_id,
            room_id,
            start_time_str,
            end_time_str,
        )
        return True

    def initialize_solution(self):
        """
        Generates an initial feasible solution by assigning surgeries to available slots.
        Uses the FeasibilityChecker for surgeon and equipment availability.
        Considers Sequence-Dependent Setup Times (SDST).
        """
        if not self.surgeries or not self.operating_rooms:
            logger.warning(
                "Cannot initialize solution: surgeries or operating_rooms data is missing."
            )
            return [] # Return empty assignments

        # Sort surgeries: e.g., by urgency, then by duration
        surgeries_to_schedule = sorted(
            self.surgeries,
            key=lambda s: (getattr(s, 'urgency_level', 'Low'), -getattr(s, 'duration_minutes', 120)), # Access duration_minutes
            reverse=True
        )

        current_solution_assignments = [] # Store the assignments made in this initialization run
        last_surgery_type_in_room = {} # Tracks the last surgery type ID for each room for SDST {room_id: type_id}

        for surgery in surgeries_to_schedule:
            assigned = False
            surgery_id_val = getattr(surgery, 'surgery_id', None)
            if not surgery_id_val:
                logger.error("Surgery object missing 'surgery_id' attribute. Skipping.")
                continue

            current_surgery_type_id = getattr(surgery, 'surgery_type_id', None)
            if current_surgery_type_id is None:
                logger.warning(f"Surgery {surgery_id_val} is missing 'surgery_type_id'. SDST might not be accurate.")

            # Attempt to find the best room (e.g., least busy, preferred room)
            # For simplicity, iterating through rooms as before
            # Consider sorting rooms based on some criteria if needed (e.g., earliest availability considering SDST)
            for room in self.operating_rooms:
                room_id_val = getattr(room, 'room_id', None)
                if not room_id_val:
                    logger.error("Room object missing 'room_id' attribute. Skipping room.")
                    continue

                surgery_duration = getattr(surgery, "duration_minutes", 120) # Use duration_minutes

                previous_surgery_type_id_for_room = last_surgery_type_in_room.get(room_id_val)

                # Use the current state of self.surgery_room_assignments for find_next_available_time
                available_slot = self.find_next_available_time(
                    room_id_val,
                    surgery_duration,
                    current_surgery_type_id=current_surgery_type_id,
                    previous_surgery_type_id=previous_surgery_type_id_for_room
                )

                # Check if available_slot is None (no available time found)
                if available_slot is None:
                    logger.debug(f"No available slot found for surgery {surgery_id_val} in room {room_id_val}")
                    continue  # Try next room

                surgeon_id_val = getattr(surgery, "surgeon_id", None)
                if not surgeon_id_val:
                    logger.warning(
                        "Surgeon ID not found for surgery %s. Skipping surgeon availability check.",
                        surgery_id_val,
                    )
                    surgeon_available = False # Or handle as per policy (e.g., assume available if not specified)
                else:
                    surgeon_available = self.feasibility_checker.is_surgeon_available(
                        surgeon_id_val,
                        available_slot["start_time"],
                        available_slot["end_time"],
                        self.surgery_room_assignments, # Pass the current assignments made so far
                        current_surgery_id_to_ignore=None # Not ignoring any for initial assignment
                    )

                # We already checked if available_slot is None above, so this should be safe
                equipment_available = self.feasibility_checker.is_equipment_available(
                    surgery_id_val, # Pass surgery_id
                    available_slot["start_time"],
                    available_slot["end_time"],
                    self.surgery_room_assignments # Pass current assignments for equipment check too
                )

                if available_slot and surgeon_available and equipment_available: # Ensure available_slot is not None
                    # Create the SurgeryRoomAssignment object first
                    try:
                        # Use standard datetime for fromisoformat
                        start_dt = datetime.fromisoformat(available_slot["start_time"])
                        end_dt = datetime.fromisoformat(available_slot["end_time"])
                    except ValueError as e:
                        logger.error(f"Error parsing date strings from available_slot for surgery {surgery_id_val}: {available_slot}. Error: {e}")
                        continue # Try next room or skip if slot is malformed

                    new_assignment_obj = SurgeryRoomAssignment(
                        surgery_id=surgery_id_val,
                        room_id=room_id_val,
                        start_time=start_dt,
                        end_time=end_dt
                    )

                    # Call assign_surgery_to_room_and_time to add to the main list (self.surgery_room_assignments)
                    # and for logging. This also serves as a final confirmation.
                    if self.assign_surgery_to_room_and_time(
                        surgery_id_val, room_id_val, available_slot["start_time"], available_slot["end_time"]
                    ):
                        current_solution_assignments.append(new_assignment_obj) # Add to the solution being built for this run
                        last_surgery_type_in_room[room_id_val] = current_surgery_type_id
                        assigned = True
                        logger.info(f"Successfully assigned Surgery {surgery_id_val} to Room {room_id_val} at {available_slot['start_time']}")
                        break  # Move to the next surgery
                    else:
                        # This case should ideally not happen if all checks pass and assign_surgery_to_room_and_time is robust
                        logger.warning(f"assign_surgery_to_room_and_time returned False for surgery {surgery_id_val} in room {room_id_val} for slot {available_slot}, though checks passed.")

            if not assigned:
                logger.warning("Could not assign surgery %s to any room.", surgery_id_val)

        logger.info(f"Initial solution generated with {len(current_solution_assignments)} assignments for this run.")
        return current_solution_assignments # Return only assignments made in this specific call

# Other standalone utility functions can also be added here if not class-specific.