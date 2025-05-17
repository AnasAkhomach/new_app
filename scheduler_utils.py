# This file will contain utility functions for the scheduler.
import logging
from datetime import datetime, timedelta
from models import SurgeryRoomAssignment # Assuming models.py is in the same directory or accessible

logger = logging.getLogger(__name__)

class SchedulerUtils:
    def __init__(self, db_session, surgeries, operating_rooms, feasibility_checker, surgery_equipments, surgery_equipment_usages):
        self.db_session = db_session
        self.surgeries = surgeries # List of Surgery objects
        self.operating_rooms = operating_rooms # List of OperatingRoom objects
        self.feasibility_checker = feasibility_checker # Instance of FeasibilityChecker
        self.surgery_room_assignments = [] # In-memory list of SurgeryRoomAssignment objects for the current run
        self.surgery_equipments = surgery_equipments
        self.surgery_equipment_usages = surgery_equipment_usages
        logger.info("SchedulerUtils initialized.")

    def find_next_available_time(self, room_id, surgery_duration_minutes):
        """Finds the next available time slot in a room, considering setup and cleanup."""
        # from datetime import time # Ensure time is imported if used, but datetime.min.time() is better

        setup_time = timedelta(minutes=15)
        cleanup_time = timedelta(minutes=15)
        now = datetime.now()
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
        if hasattr(room, "availability_start_time") and room.availability_start_time:
            if isinstance(room.availability_start_time, datetime):
                 room_operational_start_dt = datetime.combine(today, room.availability_start_time.time())
            elif isinstance(room.availability_start_time, str):
                try:
                    parsed_room_start_time = datetime.strptime(room.availability_start_time, "%H:%M:%S").time()
                    room_operational_start_dt = datetime.combine(today, parsed_room_start_time)
                except ValueError:
                    logger.warning(
                        "Room %s availability_start_time string '%s' is invalid. Defaulting to midnight for today.",
                        room_id, room.availability_start_time
                    )
            else: # Handle cases where it might be a Python time object
                try:
                    room_operational_start_dt = datetime.combine(today, room.availability_start_time)
                except TypeError:
                     logger.warning(
                        "Room %s availability_start_time type '%s' is not directly combinable. Defaulting to midnight for today.",
                        room_id, type(room.availability_start_time)
                    )
        else:
            logger.info(
                "Room %s availability_start_time not set or is None. Defaulting to midnight for today.",
                room_id
            )

        latest_end_time = room_operational_start_dt

        if self.db_session:
            try:
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
        next_available_start = max(now if potential_start_time.date() == now.date() else potential_start_time, potential_start_time) + setup_time

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
            start_dt = datetime.fromisoformat(start_time_str) if isinstance(start_time_str, str) else start_time_str
            end_dt = datetime.fromisoformat(end_time_str) if isinstance(end_time_str, str) else end_time_str
        except ValueError as e:
            logger.error(f"Error parsing date strings for assignment: {start_time_str}, {end_time_str}. Error: {e}")
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
        """
        if not self.surgeries or not self.operating_rooms:
            logger.warning(
                "Cannot initialize solution: surgeries or operating_rooms data is missing."
            )
            return [] # Return empty assignments

        # Sort surgeries: e.g., by urgency, then by duration (shorter first to fill gaps, or longer first)
        # Using urgency from the Surgery object if available
        surgeries_to_schedule = sorted(
            self.surgeries,
            key=lambda s: (getattr(s, 'urgency_level', 0), -getattr(s, 'duration', 120)),
            reverse=True
        )

        current_assignments = [] # Store the assignments made in this initialization

        for surgery in surgeries_to_schedule:
            assigned = False
            surgery_id_val = getattr(surgery, 'id', getattr(surgery, 'surgery_id', None))
            if not surgery_id_val:
                logger.error("Surgery object missing 'id' or 'surgery_id' attribute. Skipping.")
                continue

            # Attempt to find the best room (e.g., least busy, preferred room)
            # For simplicity, iterating through rooms as before
            for room in self.operating_rooms:
                room_id_val = getattr(room, 'id', getattr(room, 'room_id', None))
                if not room_id_val:
                    logger.error("Room object missing 'id' or 'room_id' attribute. Skipping room.")
                    continue

                surgery_duration = getattr(surgery, "duration", 120) # Default duration if not specified

                # Use the current state of self.surgery_room_assignments for find_next_available_time
                available_slot = self.find_next_available_time(
                    room_id_val, surgery_duration
                )

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

                equipment_available = self.feasibility_checker.is_equipment_available(
                    surgery_id_val, # Pass surgery_id
                    available_slot["start_time"],
                    available_slot["end_time"],
                    self.surgery_room_assignments # Pass current assignments for equipment check too
                )

                if surgeon_available and equipment_available:
                    # Use the class's assign_surgery_to_room_and_time which updates self.surgery_room_assignments
                    assignment_successful = self.assign_surgery_to_room_and_time(
                        surgery_id_val,
                        room_id_val,
                        available_slot["start_time"],
                        available_slot["end_time"],
                    )
                    if assignment_successful:
                        # The assign method already appends to self.surgery_room_assignments
                        # We can add to a local list if we want to return only newly made assignments
                        newly_made_assignment = self.surgery_room_assignments[-1] # Get the last added one
                        current_assignments.append(newly_made_assignment)
                        assigned = True
                        logger.info(f"Successfully assigned Surgery {surgery_id_val} to Room {room_id_val} at {available_slot['start_time']}")
                        break # Move to the next surgery

            if not assigned:
                logger.warning("Could not assign surgery %s to any room.", surgery_id_val)

        logger.info(f"Initial solution generated with {len(self.surgery_room_assignments)} assignments.")
        return self.surgery_room_assignments # Return all assignments made by the class instance

# Other standalone utility functions can also be added here if not class-specific.