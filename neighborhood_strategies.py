# This file will contain the logic for generating neighborhood solutions.
import random
import copy # For deep copying solutions
import logging
from datetime import datetime, timedelta
from models import SurgeryRoomAssignment # Assuming models.py is accessible

logger = logging.getLogger(__name__)

class NeighborhoodStrategies:
    def __init__(self, db_session, surgeries_data, operating_rooms_data, surgeons_data, feasibility_checker, scheduler_utils, sds_times_data):
        self.db_session = db_session
        self.surgeries_data = surgeries_data # List of Surgery objects/data
        self.operating_rooms_data = operating_rooms_data # List of OR objects/data
        self.surgeons_data = surgeons_data # List of Surgeon objects/data
        self.feasibility_checker = feasibility_checker # Instance of FeasibilityChecker
        self.scheduler_utils = scheduler_utils # Instance of SchedulerUtils, expected to be SDST-aware
        self.sds_times_data = sds_times_data # {(from_type_id, to_type_id): setup_minutes}
        logger.info("NeighborhoodStrategies initialized with SDST data.")

        self.surgery_id_to_type_id_map = {}

    def initialize_solution_randomly(self):
        """
        Generates a new, diverse, and feasible initial solution randomly.
        This is a placeholder and would require significant logic based on problem constraints.
        It should try to create a valid schedule from scratch, possibly using some heuristics
        or a simplified version of the initial solution generation logic in SchedulerUtils.
        The goal is to provide a significantly different starting point for diversification.
        """
        logger.info("Attempting to initialize a solution randomly (placeholder).")
        # Placeholder: returns a deepcopy of a potentially pre-defined 'default' or 'empty' schedule
        # or uses a simplified random assignment logic.
        # In a real implementation, this would involve:
        # 1. Getting all available surgeries (self.surgeries_data).
        # 2. Iterating through them and randomly assigning to rooms (self.operating_rooms_data)
        #    and finding a feasible time slot using self.scheduler_utils.find_next_available_time.
        # 3. Ensuring overall feasibility with self.feasibility_checker.
        # For now, let's assume it might call a simplified version of what SchedulerUtils.initialize_solution does,
        # but with more randomness or by picking a subset of surgeries.

        # Fallback: If a true random generation is too complex for a placeholder,
        # it could return a pre-defined 'seed' solution or even the original initial solution
        # passed to TabuSearchCore, though the latter is less effective for diversification.

        # For this placeholder, we'll simulate creating a very simple, potentially sparse schedule.
        # This is NOT a robust implementation for a real system.
        new_random_assignments = []
        if not self.surgeries_data or not self.operating_rooms_data:
            logger.warning("Cannot generate random solution: missing surgeries or rooms data.")
            return []

        # Attempt to schedule a small subset of surgeries randomly as a basic example
        surgeries_to_schedule = random.sample(self.surgeries_data, min(len(self.surgeries_data), 5)) # Schedule up to 5
        temp_schedule = []

        for surgery_obj in surgeries_to_schedule:
            surgery_id_str = str(getattr(surgery_obj, 'id', None))
            if not surgery_id_str: continue

            surgery_duration_minutes = getattr(surgery_obj, 'expected_duration_minutes', 120) # Default if not found
            current_surgery_type_id = self._get_surgery_type_id(surgery_id_str)

            available_rooms = list(self.operating_rooms_data)
            random.shuffle(available_rooms)
            assigned_to_room = False
            for room_obj in available_rooms:
                room_id_str = str(getattr(room_obj, 'id', None))
                if not room_id_str: continue

                # Simplified: try to find a slot starting from a common time, e.g., 8 AM
                preferred_start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

                last_surgery_in_room_type_id = None # Simplified for placeholder
                # In a real scenario, you'd check temp_schedule for last surgery in this room

                slot = self.scheduler_utils.find_next_available_time(
                    room_id=int(room_id_str),
                    preferred_start_time=preferred_start_time,
                    surgery_duration_minutes=int(surgery_duration_minutes),
                    schedule_assignments=temp_schedule, # Check against already placed surgeries in this random batch
                    surgery_id_to_check=surgery_id_str,
                    last_surgery_type_in_room_id=last_surgery_in_room_type_id,
                    current_surgery_type_id=current_surgery_type_id
                )
                if slot:
                    new_assignment = SurgeryRoomAssignment(
                        surgery_id=int(surgery_id_str) if surgery_id_str.isdigit() else None,
                        room_id=int(room_id_str),
                        start_time=slot['start_time'],
                        end_time=slot['end_time'],
                        surgeon_id=getattr(surgery_obj, 'preferred_surgeon_id', None) # Simplified surgeon assignment
                    )
                    temp_schedule.append(new_assignment)
                    assigned_to_room = True
                    break # Assigned to a room
            if not assigned_to_room:
                logger.warning(f"Could not randomly assign surgery {surgery_id_str} to any room (placeholder logic).")

        if self.feasibility_checker.is_feasible(temp_schedule):
            logger.info(f"Placeholder initialize_solution_randomly generated a feasible schedule with {len(temp_schedule)} assignments.")
            return temp_schedule
        else:
            logger.warning("Placeholder initialize_solution_randomly generated an INFEASIBLE schedule. Returning empty.")
            return [] # Fallback if generated schedule is not feasible

        self.surgery_id_to_type_id_map = {}
        for surgery in self.surgeries_data:
            # Assuming surgery objects have 'id' and 'surgery_type_id' (after models.py update)
            # or 'surgery_type' object with 'type_id'
            s_id = getattr(surgery, 'id', None)
            s_type_id = getattr(surgery, 'surgery_type_id', None)
            if s_id is not None and s_type_id is not None:
                self.surgery_id_to_type_id_map[str(s_id)] = s_type_id
            elif s_id is not None and hasattr(surgery, 'surgery_type') and hasattr(surgery.surgery_type, 'type_id'):
                self.surgery_id_to_type_id_map[str(s_id)] = surgery.surgery_type.type_id
            else:
                logger.warning(f"Could not determine surgery type ID for surgery {s_id or 'N/A'} during NeighborhoodStrategies init.")

    def _get_surgery_type_id(self, surgery_id_str):
        """Helper to get surgery_type_id from surgery_id string."""
        return self.surgery_id_to_type_id_map.get(str(surgery_id_str))

    def _get_sds_time(self, from_surgery_type_id, to_surgery_type_id):
        """Get sequence-dependent setup time in minutes."""
        if from_surgery_type_id is None or to_surgery_type_id is None:
            return 0
        return self.sds_times_data.get((from_surgery_type_id, to_surgery_type_id), 0)

    def generate_neighbor_solutions(self, current_schedule_assignments, tabu_list):
        """Generates a list of neighbor solutions from the current schedule."""
        neighbors = []
        if not self.surgeries_data or not current_schedule_assignments:
            logger.warning("Cannot generate neighbors: no surgeries or empty current schedule.")
            return neighbors

        # Sample surgeries once for all strategies that use sampling
        # Ensure there are surgeries to sample from; current_schedule_assignments implies surgeries exist
        # We need to map surgery_ids from current_schedule_assignments back to full surgery objects from self.surgeries_data

        # Get full surgery objects for those in the current schedule
        scheduled_surgery_ids = {str(asn.surgery_id) for asn in current_schedule_assignments if hasattr(asn, 'surgery_id') and asn.surgery_id is not None}
        surgeries_in_schedule = [s for s in self.surgeries_data if hasattr(s, 'id') and str(s.id) in scheduled_surgery_ids or hasattr(s, 'surgery_id') and str(s.surgery_id) in scheduled_surgery_ids]

        if not surgeries_in_schedule:
            logger.warning("No valid surgeries found in the current schedule to generate neighbors from.")
            return neighbors

        sampled_surgeries_for_strategies = random.sample(
            surgeries_in_schedule, min(len(surgeries_in_schedule), 10)
        ) if surgeries_in_schedule else []

        # Strategy 1: Move Surgery to a Different Room (SDST Aware)
        logger.debug("Generating neighbors: Strategy 1 - Move Surgery to a Different Room (SDST Aware)")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(surgery_obj.id if hasattr(surgery_obj, 'id') else getattr(surgery_obj, 'surgery_id', None))
            current_assignment_obj = next((
                asn_obj for asn_obj in current_schedule_assignments if hasattr(asn_obj, 'surgery_id') and str(asn_obj.surgery_id) == surgery_id_str
            ), None)
            if not current_assignment_obj: continue

            if not all(hasattr(current_assignment_obj, attr) for attr in ['start_time', 'end_time', 'room_id', 'surgery_id', 'surgeon_id']):
                logger.warning(f"Skipping move for surgery {surgery_id_str} due to missing attributes in current assignment: {current_assignment_obj}")
                continue

            original_room_id_str = str(current_assignment_obj.room_id)
            original_start_time = current_assignment_obj.start_time # datetime object
            surgery_duration_minutes = (current_assignment_obj.end_time - original_start_time).total_seconds() / 60
            current_surgery_type_id = self._get_surgery_type_id(surgery_id_str)
            current_surgeon_id = current_assignment_obj.surgeon_id

            possible_rooms = [r for r in self.operating_rooms_data if hasattr(r, 'id') and str(r.id) != original_room_id_str]
            random.shuffle(possible_rooms)

            for target_room_obj in possible_rooms[:min(len(possible_rooms), 2)]:
                target_room_id_str = str(target_room_obj.id)

                # Determine the last surgery type in the target_room before the potential move
                last_surgery_in_target_room_type_id = None
                # Consider only assignments in the target room, excluding the one being moved (if it was there hypothetically)
                # and sort them by end time to find the latest one before a preferred start.
                relevant_assignments_in_target_room = sorted([
                    asn for asn in current_schedule_assignments
                    if hasattr(asn, 'room_id') and str(asn.room_id) == target_room_id_str and
                       hasattr(asn, 'surgery_id') and str(asn.surgery_id) != surgery_id_str and \
                       hasattr(asn, 'end_time')
                ], key=lambda x: x.end_time)

                if relevant_assignments_in_target_room:
                    # This logic might need to be more nuanced: find the one immediately preceding the *potential* new slot.
                    # For now, using the type of the last known surgery in that room.
                    last_surgery_in_target_room_type_id = self._get_surgery_type_id(str(relevant_assignments_in_target_room[-1].surgery_id))

                # Use SDST-aware find_next_available_time
                # Preferred start time could be the original start time, or a time based on operational hours.
                found_slot = self.scheduler_utils.find_next_available_time(
                    room_id=int(target_room_id_str),
                    preferred_start_time=original_start_time, # Try to keep original time if possible
                    surgery_duration_minutes=int(surgery_duration_minutes),
                    # Pass schedule excluding the current surgery's original assignment, as it's being moved
                    schedule_assignments=[asn for asn in current_schedule_assignments if hasattr(asn, 'surgery_id') and str(asn.surgery_id) != surgery_id_str],
                    surgery_id_to_check=surgery_id_str, # ID of surgery being moved
                    last_surgery_type_in_room_id=last_surgery_in_target_room_type_id,
                    current_surgery_type_id=current_surgery_type_id
                )

                if found_slot:
                    new_start_dt = found_slot['start_time']
                    new_end_dt = found_slot['end_time']
                else:
                    logger.debug(f"No SDST-aware slot found for surgery {surgery_id_str} in room {target_room_id_str}.")
                    continue

                move_attribute = ("move_surgery_room_sds", surgery_id_str, target_room_id_str, new_start_dt.isoformat())
                if tabu_list.is_tabu(move_attribute):
                    logger.debug(f"SDST-aware Move for surgery {surgery_id_str} to room {target_room_id_str} at {new_start_dt.isoformat()} is TABU.")
                    continue

                new_assignment = SurgeryRoomAssignment(
                    surgery_id=int(surgery_id_str) if surgery_id_str.isdigit() else None,
                    room_id=int(target_room_id_str),
                    start_time=new_start_dt,
                    end_time=new_end_dt,
                    surgeon_id=current_surgeon_id
                )

                temp_neighbor_assignments = [asn for asn in current_schedule_assignments if hasattr(asn, 'surgery_id') and str(asn.surgery_id) != surgery_id_str]
                temp_neighbor_assignments.append(new_assignment)

                if self.feasibility_checker.is_feasible(temp_neighbor_assignments):
                    neighbors.append({"assignments": temp_neighbor_assignments, "move": move_attribute})
                    logger.debug(f"Generated SDST-aware MOVE_ROOM neighbor: Surgery {surgery_id_str} to Room {target_room_id_str} at {new_start_dt.isoformat()}")
                else:
                    logger.debug(f"SDST-aware Move for {surgery_id_str} to room {target_room_id_str} resulted in infeasible schedule.")

        # Strategy 2: Swap Two Surgeries (SDST Aware)
        logger.debug("Generating neighbors: Strategy 2 - Swap Two Surgeries (SDST Aware)")
        if len(current_schedule_assignments) >= 2:
            potential_pairs = list(itertools.combinations(current_schedule_assignments, 2))
            random.shuffle(potential_pairs)

            for asn1_obj, asn2_obj in potential_pairs[:min(len(potential_pairs), 5)]: # Try up to 5 distinct pairs for swapping
                if not (hasattr(asn1_obj, 'surgery_id') and hasattr(asn2_obj, 'surgery_id') and
                        hasattr(asn1_obj, 'room_id') and hasattr(asn2_obj, 'room_id') and
                        hasattr(asn1_obj, 'start_time') and hasattr(asn2_obj, 'start_time') and
                        hasattr(asn1_obj, 'end_time') and hasattr(asn2_obj, 'end_time') and
                        hasattr(asn1_obj, 'surgeon_id') and hasattr(asn2_obj, 'surgeon_id')):
                    logger.warning(f"Skipping swap pair due to missing critical attributes in assignments: {asn1_obj}, {asn2_obj}")
                    continue

                surgery1_id_str = str(asn1_obj.surgery_id)
                surgery2_id_str = str(asn2_obj.surgery_id)

                s1_type_id = self._get_surgery_type_id(surgery1_id_str)
                s2_type_id = self._get_surgery_type_id(surgery2_id_str)

                s1_duration_minutes = (asn1_obj.end_time - asn1_obj.start_time).total_seconds() / 60
                s2_duration_minutes = (asn2_obj.end_time - asn2_obj.start_time).total_seconds() / 60

                s1_orig_room_id, s1_orig_start_time, s1_orig_surgeon_id = asn1_obj.room_id, asn1_obj.start_time, asn1_obj.surgeon_id
                s2_orig_room_id, s2_orig_start_time, s2_orig_surgeon_id = asn2_obj.room_id, asn2_obj.start_time, asn2_obj.surgeon_id

                # Create a temporary schedule without s1 and s2 to find preceding surgeries for their new slots
                base_schedule_for_swap = [asn for asn in current_schedule_assignments
                                          if hasattr(asn, 'surgery_id') and str(asn.surgery_id) not in [surgery1_id_str, surgery2_id_str]]

                # Determine preceding surgery for s1 in s2's original slot
                last_s_before_s1_in_s2_slot_type_id = None
                relevant_for_s1_new_slot = sorted([
                    asn for asn in base_schedule_for_swap
                    if hasattr(asn, 'room_id') and asn.room_id == s2_orig_room_id and hasattr(asn, 'end_time') and asn.end_time < s2_orig_start_time
                ], key=lambda x: x.end_time)
                if relevant_for_s1_new_slot:
                    last_s_before_s1_in_s2_slot_type_id = self._get_surgery_type_id(str(relevant_for_s1_new_slot[-1].surgery_id))

                # Determine preceding surgery for s2 in s1's original slot
                last_s_before_s2_in_s1_slot_type_id = None
                relevant_for_s2_new_slot = sorted([
                    asn for asn in base_schedule_for_swap
                    if hasattr(asn, 'room_id') and asn.room_id == s1_orig_room_id and hasattr(asn, 'end_time') and asn.end_time < s1_orig_start_time
                ], key=lambda x: x.end_time)
                if relevant_for_s2_new_slot:
                    last_s_before_s2_in_s1_slot_type_id = self._get_surgery_type_id(str(relevant_for_s2_new_slot[-1].surgery_id))

                # Calculate new slot for s1 (in s2's original room and preferred start time)
                s1_new_slot_info = self.scheduler_utils.find_next_available_time(
                    room_id=s2_orig_room_id, preferred_start_time=s2_orig_start_time, surgery_duration_minutes=int(s1_duration_minutes),
                    schedule_assignments=base_schedule_for_swap, surgery_id_to_check=surgery1_id_str,
                    last_surgery_type_in_room_id=last_s_before_s1_in_s2_slot_type_id, current_surgery_type_id=s1_type_id
                )
                # Calculate new slot for s2 (in s1's original room and preferred start time)
                s2_new_slot_info = self.scheduler_utils.find_next_available_time(
                    room_id=s1_orig_room_id, preferred_start_time=s1_orig_start_time, surgery_duration_minutes=int(s2_duration_minutes),
                    schedule_assignments=base_schedule_for_swap, surgery_id_to_check=surgery2_id_str,
                    last_surgery_type_in_room_id=last_s_before_s2_in_s1_slot_type_id, current_surgery_type_id=s2_type_id
                )

                if not s1_new_slot_info or not s2_new_slot_info:
                    logger.debug(f"Could not find SDST-aware slots for swap between {surgery1_id_str} and {surgery2_id_str}.")
                    continue

                new_s1_start_time, new_s1_end_time = s1_new_slot_info['start_time'], s1_new_slot_info['end_time']
                new_s2_start_time, new_s2_end_time = s2_new_slot_info['start_time'], s2_new_slot_info['end_time']

                # Create new assignment objects
                new_s1_assignment = SurgeryRoomAssignment(
                    surgery_id=int(surgery1_id_str), room_id=s2_orig_room_id, start_time=new_s1_start_time,
                    end_time=new_s1_end_time, surgeon_id=s1_orig_surgeon_id
                )
                new_s2_assignment = SurgeryRoomAssignment(
                    surgery_id=int(surgery2_id_str), room_id=s1_orig_room_id, start_time=new_s2_start_time,
                    end_time=new_s2_end_time, surgeon_id=s2_orig_surgeon_id
                )

                move_attribute = (
                    "swap_surgeries_sds", frozenset({surgery1_id_str, surgery2_id_str}),
                    str(new_s1_assignment.room_id), new_s1_assignment.start_time.isoformat(),
                    str(new_s2_assignment.room_id), new_s2_assignment.start_time.isoformat()
                )
                if tabu_list.is_tabu(move_attribute):
                    logger.debug(f"SDST-aware Swap for {surgery1_id_str} & {surgery2_id_str} is TABU: {move_attribute}")
                    continue

                temp_neighbor_assignments = list(base_schedule_for_swap) # Start with assignments other than s1, s2
                temp_neighbor_assignments.extend([new_s1_assignment, new_s2_assignment])

                if self.feasibility_checker.is_feasible(temp_neighbor_assignments):
                    neighbors.append({"assignments": temp_neighbor_assignments, "move": move_attribute})
                    logger.debug(f"Generated SDST-aware SWAP: {surgery1_id_str} (to room {new_s1_assignment.room_id} at {new_s1_assignment.start_time.isoformat()}) with {surgery2_id_str} (to room {new_s2_assignment.room_id} at {new_s2_assignment.start_time.isoformat()})")
                else:
                    logger.debug(f"SDST-aware Swap for {surgery1_id_str} & {surgery2_id_str} resulted in infeasible schedule.")

        # Strategy 3: Shift Surgery Time within the same room (SDST Aware)
        logger.debug("Generating neighbors: Strategy 3 - Shift Surgery Time (SDST Aware)")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(surgery_obj.id if hasattr(surgery_obj, 'id') else getattr(surgery_obj, 'surgery_id', None))
            current_assignment_obj = next((asn_obj for asn_obj in current_schedule_assignments if hasattr(asn_obj, 'surgery_id') and str(asn_obj.surgery_id) == surgery_id_str), None)
            if not current_assignment_obj: continue

            if not all(hasattr(current_assignment_obj, attr) for attr in ['start_time', 'end_time', 'room_id', 'surgery_id', 'surgeon_id']):
                logger.warning(f"Skipping SDST-aware shift for surgery {surgery_id_str} due to missing attributes: {current_assignment_obj}")
                continue

            current_room_id = current_assignment_obj.room_id
            original_start_dt = current_assignment_obj.start_time
            original_end_dt = current_assignment_obj.end_time
            surgery_duration_minutes = (original_end_dt - original_start_dt).total_seconds() / 60
            current_surgery_type_id = self._get_surgery_type_id(surgery_id_str)
            current_surgeon_id = current_assignment_obj.surgeon_id

            # Base schedule excluding the surgery being shifted
            base_schedule_for_shift = [asn for asn in current_schedule_assignments if hasattr(asn, 'surgery_id') and str(asn.surgery_id) != surgery_id_str]

            # Try shifting earlier and later by finding next available slot around original time
            potential_preferred_starts = [
                original_start_dt,
                original_start_dt - timedelta(minutes=30),
                original_start_dt + timedelta(minutes=30),
                original_start_dt - timedelta(minutes=60),
                original_start_dt + timedelta(minutes=60)
            ]
            random.shuffle(potential_preferred_starts)

            for preferred_start_attempt in potential_preferred_starts[:3]: # Try up to 3 different preferred starts
                # Determine the last surgery type in the room before this potential new start time
                last_surgery_type_before_new_slot = None
                relevant_surgeries_before = sorted([
                    asn for asn in base_schedule_for_shift
                    if hasattr(asn, 'room_id') and asn.room_id == current_room_id and
                       hasattr(asn, 'end_time') and asn.end_time <= preferred_start_attempt # Consider surgeries ending before or at preferred start
                ], key=lambda x: x.end_time)
                if relevant_surgeries_before:
                    last_surgery_type_before_new_slot = self._get_surgery_type_id(str(relevant_surgeries_before[-1].surgery_id))

                found_slot = self.scheduler_utils.find_next_available_time(
                    room_id=current_room_id,
                    preferred_start_time=preferred_start_attempt,
                    surgery_duration_minutes=int(surgery_duration_minutes),
                    schedule_assignments=base_schedule_for_shift, # Pass schedule without the current surgery
                    surgery_id_to_check=surgery_id_str,
                    last_surgery_type_in_room_id=last_surgery_type_before_new_slot,
                    current_surgery_type_id=current_surgery_type_id
                )

                if found_slot:
                    new_start_dt = found_slot['start_time']
                    new_end_dt = found_slot['end_time']

                    if new_start_dt == original_start_dt:
                        logger.debug(f"SDST-aware shift for {surgery_id_str} resulted in the same slot. Skipping.")
                        continue
                else:
                    logger.debug(f"No SDST-aware slot found for shifting {surgery_id_str} around {preferred_start_attempt.isoformat()} in room {current_room_id}.")
                    continue

                move_attribute = ("shift_time_sds", surgery_id_str, str(current_room_id), new_start_dt.isoformat())
                if tabu_list.is_tabu(move_attribute):
                    logger.debug(f"SDST-aware Shift for {surgery_id_str} to {new_start_dt.isoformat()} in room {current_room_id} is TABU.")
                    continue

                new_assignment = SurgeryRoomAssignment(
                    surgery_id=int(surgery_id_str),
                    room_id=current_room_id,
                    start_time=new_start_dt,
                    end_time=new_end_dt,
                    surgeon_id=current_surgeon_id
                )
                temp_neighbor_assignments = list(base_schedule_for_shift)
                temp_neighbor_assignments.append(new_assignment)

                if self.feasibility_checker.is_feasible(temp_neighbor_assignments):
                    neighbors.append({"assignments": temp_neighbor_assignments, "move": move_attribute})
                    logger.debug(f"Generated SDST-aware SHIFT neighbor: Surgery {surgery_id_str} in Room {current_room_id} to {new_start_dt.isoformat()}")
                else:
                    logger.debug(f"SDST-aware Shift for {surgery_id_str} to {new_start_dt.isoformat()} resulted in infeasible schedule.")


        # Strategy 4: Change Surgeon
        logger.debug("Generating neighbors: Strategy 4 - Change Surgeon")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(surgery_obj.id if hasattr(surgery_obj, 'id') else getattr(surgery_obj, 'surgery_id', None))
            current_assignment_obj = next((asn for asn in current_schedule_assignments if hasattr(asn, 'surgery_id') and str(asn.surgery_id) == surgery_id_str), None)
            if not current_assignment_obj: continue

            if not all(hasattr(current_assignment_obj, attr) for attr in ['surgery_id', 'room_id', 'start_time', 'end_time', 'surgeon_id']):
                logger.warning(f"Skipping change surgeon for surgery {surgery_id_str} due to missing attributes in its assignment.")
                continue

            original_surgeon_id_str = str(current_assignment_obj.surgeon_id)
            surgery_type = getattr(surgery_obj, 'surgery_type', 'General') # Assuming a 'surgery_type' attribute

            # Find alternative qualified surgeons (excluding the original surgeon)
            # This requires knowledge of surgeon qualifications for surgery_type.
            # For now, let's assume self.surgeons_data contains all surgeons and we can pick any other one.
            # In a real system, this would involve checking a qualifications mapping.
            alternative_surgeons = [
                s for s in self.surgeons_data
                if hasattr(s, 'id') and str(s.id) != original_surgeon_id_str # and self.is_qualified(s, surgery_type)
            ]
            random.shuffle(alternative_surgeons)

            for new_surgeon_obj in alternative_surgeons[:min(len(alternative_surgeons), 2)]: # Try up to 2 alternative surgeons
                new_surgeon_id_str = str(new_surgeon_obj.id if hasattr(new_surgeon_obj, 'id') else None)
                if not new_surgeon_id_str: continue

                # Define tabu attribute: (action_type, surgery_id, new_surgeon_id)
                move_attribute = ("change_surgeon", surgery_id_str, new_surgeon_id_str)
                if tabu_list.is_tabu(move_attribute):
                    logger.debug(f"Change surgeon for surgery {surgery_id_str} to {new_surgeon_id_str} is TABU.")
                    continue

                neighbor_assignments_change_surgeon_list = copy.deepcopy(current_schedule_assignments)
                assignment_to_change_in_neighbor = next((na for na in neighbor_assignments_change_surgeon_list if hasattr(na, 'surgery_id') and str(na.surgery_id) == surgery_id_str), None)
                if not assignment_to_change_in_neighbor: continue

                assignment_to_change_in_neighbor.surgeon_id = int(new_surgeon_id_str) if new_surgeon_id_str.isdigit() else None
                # Room, start_time, end_time remain the same for this move

                if self.feasibility_checker.is_feasible(neighbor_assignments_change_surgeon_list):
                    neighbors.append({"assignments": neighbor_assignments_change_surgeon_list, "move": move_attribute})
                    logger.debug(f"Generated CHANGE SURGEON neighbor: Surgery {surgery_id_str} to Surgeon {new_surgeon_id_str}")
                else:
                    logger.debug(f"Change surgeon for surgery {surgery_id_str} to {new_surgeon_id_str} resulted in infeasible schedule.")

        # Strategy 4: Change Surgeon ... (Code for strategy 4 remains here, unchanged for SDST)
        # ... (existing code for Strategy 4)

        # Strategy 5: Reschedule to Specific Time Slot (SDST Aware)
        logger.debug("Generating neighbors: Strategy 5 - Reschedule to Specific Time Slot (SDST Aware)")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(getattr(surgery_obj, 'id', getattr(surgery_obj, 'surgery_id', None)))
            current_assignment_obj = next((ra_obj for ra_obj in current_schedule_assignments if hasattr(ra_obj, 'surgery_id') and str(ra_obj.surgery_id) == surgery_id_str), None)
            if not current_assignment_obj: continue

            if not all(hasattr(current_assignment_obj, attr) for attr in ['start_time', 'end_time', 'room_id', 'surgery_id', 'surgeon_id']):
                logger.warning(f"Skipping SDST-aware reschedule for surgery {surgery_id_str} due to missing attributes: {current_assignment_obj}")
                continue

            original_start_dt = current_assignment_obj.start_time
            original_end_dt = current_assignment_obj.end_time
            surgery_duration_minutes = int((original_end_dt - original_start_dt).total_seconds() / 60)
            current_surgery_type_id = self._get_surgery_type_id(surgery_id_str)
            current_room_id = current_assignment_obj.room_id
            current_surgeon_id = current_assignment_obj.surgeon_id

            base_schedule_for_reschedule = [asn for asn in current_schedule_assignments if hasattr(asn, 'surgery_id') and str(asn.surgery_id) != surgery_id_str]

            time_slots_definitions = [
                {"name": "early_morning", "hour": 7, "minute": 30},
                {"name": "morning", "hour": 9, "minute": 0},
                {"name": "late_morning", "hour": 10, "minute": 30},
                {"name": "early_afternoon", "hour": 13, "minute": 0},
                {"name": "afternoon", "hour": 14, "minute": 30},
                {"name": "late_afternoon", "hour": 16, "minute": 0},
            ]
            current_date = original_start_dt.date()
            random.shuffle(time_slots_definitions)

            for slot_def in time_slots_definitions[:2]: # Try up to 2 different predefined slots
                preferred_slot_start_dt = datetime.combine(current_date, datetime.min.time().replace(hour=slot_def["hour"], minute=slot_def["minute"]))

                # Avoid rescheduling to the exact same or very similar time
                if abs((preferred_slot_start_dt - original_start_dt).total_seconds()) < 1800: # 30 minutes threshold
                    continue

                # Determine last surgery type before this preferred slot in the same room
                last_surgery_type_before_slot = None
                relevant_surgeries_before_slot = sorted([
                    asn for asn in base_schedule_for_reschedule
                    if hasattr(asn, 'room_id') and asn.room_id == current_room_id and
                       hasattr(asn, 'end_time') and asn.end_time <= preferred_slot_start_dt
                ], key=lambda x: x.end_time)
                if relevant_surgeries_before_slot:
                    last_surgery_type_before_slot = self._get_surgery_type_id(str(relevant_surgeries_before_slot[-1].surgery_id))

                found_actual_slot = self.scheduler_utils.find_next_available_time(
                    room_id=current_room_id,
                    preferred_start_time=preferred_slot_start_dt,
                    surgery_duration_minutes=surgery_duration_minutes,
                    schedule_assignments=base_schedule_for_reschedule,
                    surgery_id_to_check=surgery_id_str,
                    last_surgery_type_in_room_id=last_surgery_type_before_slot,
                    current_surgery_type_id=current_surgery_type_id
                )

                if found_actual_slot:
                    new_start_dt = found_actual_slot['start_time']
                    new_end_dt = found_actual_slot['end_time']
                else:
                    logger.debug(f"No SDST-aware slot found for rescheduling {surgery_id_str} to {slot_def['name']} slot in room {current_room_id}.")
                    continue

                move_attribute = ("reschedule_sds", surgery_id_str, str(current_room_id), new_start_dt.isoformat(), slot_def['name'])
                if tabu_list.is_tabu(move_attribute):
                    logger.debug(f"SDST-aware Reschedule for {surgery_id_str} to {slot_def['name']} at {new_start_dt.isoformat()} in room {current_room_id} is TABU.")
                    continue

                new_assignment = SurgeryRoomAssignment(
                    surgery_id=int(surgery_id_str),
                    room_id=current_room_id,
                    start_time=new_start_dt,
                    end_time=new_end_dt,
                    surgeon_id=current_surgeon_id
                )
                temp_neighbor_assignments = list(base_schedule_for_reschedule)
                temp_neighbor_assignments.append(new_assignment)

                if self.feasibility_checker.is_feasible(temp_neighbor_assignments):
                    neighbors.append({"assignments": temp_neighbor_assignments, "move": move_attribute})
                    logger.debug(f"Generated SDST-aware RESCHEDULE neighbor: {surgery_id_str} to {slot_def['name']} slot (actual: {new_start_dt.isoformat()}) in Room {current_room_id}")
                else:
                    logger.debug(f"SDST-aware Reschedule for {surgery_id_str} to {slot_def['name']} slot resulted in infeasible schedule.")
        return neighbors # Ensure this is at the correct indentation level, after all strategies.

        # Strategy 6: Prioritize Emergency Surgeries (SDST Aware - conceptual, needs careful slot finding)
        # This strategy is complex with SDST. A simple swap of times/rooms might become infeasible due to SDST.
        # A proper implementation would need to find new feasible slots for both surgeries involved in the swap,
        # considering their types and the types of surgeries preceding them in their new potential slots.
        # For now, this strategy will be simplified or marked as needing more advanced SDST integration.
        logger.debug("Generating neighbors: Strategy 6 - Prioritize Emergency Surgeries (SDST Aware - Basic Swap)")
        # Basic idea: find a high urgency surgery scheduled later than a low/medium one. Try to swap them.
        # This is a simplified version. True SDST awareness requires re-evaluating slots with find_next_available_time.

        high_urgency_scheduled = []
        low_med_urgency_scheduled = []

        for asn in current_schedule_assignments:
            if not hasattr(asn, 'surgery_id'): continue
            surgery_detail = next((s for s in self.surgeries_data if hasattr(s, 'id') and str(s.id) == str(asn.surgery_id)), None)
            if not surgery_detail or not hasattr(surgery_detail, 'urgency_level'): continue

            if surgery_detail.urgency_level == "High":
                high_urgency_scheduled.append(asn)
            elif surgery_detail.urgency_level in ["Low", "Medium"]:
                low_med_urgency_scheduled.append(asn)

        # Sort by start time to find opportunities for prioritization
        high_urgency_scheduled.sort(key=lambda x: x.start_time)
        low_med_urgency_scheduled.sort(key=lambda x: x.start_time)

        for high_asn in high_urgency_scheduled:
            for low_asn in low_med_urgency_scheduled:
                if high_asn.start_time > low_asn.start_time: # High urgency is scheduled after low/medium
                    # Attempt a swap, similar to Strategy 2 (Swap Surgeries SDST Aware)
                    s1_id_str, s2_id_str = str(high_asn.surgery_id), str(low_asn.surgery_id)
                    s1_type_id, s2_type_id = self._get_surgery_type_id(s1_id_str), self._get_surgery_type_id(s2_id_str)
                    s1_duration = (high_asn.end_time - high_asn.start_time).total_seconds() / 60
                    s2_duration = (low_asn.end_time - low_asn.start_time).total_seconds() / 60
                    s1_orig_room, s1_orig_start, s1_surgeon = high_asn.room_id, high_asn.start_time, high_asn.surgeon_id
                    s2_orig_room, s2_orig_start, s2_surgeon = low_asn.room_id, low_asn.start_time, low_asn.surgeon_id

                    base_schedule_for_prio_swap = [a for a in current_schedule_assignments if str(a.surgery_id) not in [s1_id_str, s2_id_str]]

                    # Preceding for high_asn in low_asn's slot
                    last_s_before_s1_new_slot_type_id = None
                    relevant_s1_new = sorted([a for a in base_schedule_for_prio_swap if a.room_id == s2_orig_room and a.end_time <= s2_orig_start], key=lambda x: x.end_time)
                    if relevant_s1_new: last_s_before_s1_new_slot_type_id = self._get_surgery_type_id(str(relevant_s1_new[-1].surgery_id))

                    # Preceding for low_asn in high_asn's slot
                    last_s_before_s2_new_slot_type_id = None
                    relevant_s2_new = sorted([a for a in base_schedule_for_prio_swap if a.room_id == s1_orig_room and a.end_time <= s1_orig_start], key=lambda x: x.end_time)
                    if relevant_s2_new: last_s_before_s2_new_slot_type_id = self._get_surgery_type_id(str(relevant_s2_new[-1].surgery_id))

                    s1_new_slot = self.scheduler_utils.find_next_available_time(s2_orig_room, s2_orig_start, int(s1_duration), base_schedule_for_prio_swap, s1_id_str, last_s_before_s1_new_slot_type_id, s1_type_id)
                    s2_new_slot = self.scheduler_utils.find_next_available_time(s1_orig_room, s1_orig_start, int(s2_duration), base_schedule_for_prio_swap, s2_id_str, last_s_before_s2_new_slot_type_id, s2_type_id)

                    if not s1_new_slot or not s2_new_slot: continue

                    new_s1_assign = SurgeryRoomAssignment(surgery_id=int(s1_id_str), room_id=s2_orig_room, start_time=s1_new_slot['start_time'], end_time=s1_new_slot['end_time'], surgeon_id=s1_surgeon)
                    new_s2_assign = SurgeryRoomAssignment(surgery_id=int(s2_id_str), room_id=s1_orig_room, start_time=s2_new_slot['start_time'], end_time=s2_new_slot['end_time'], surgeon_id=s2_surgeon)

                    move_attr = ("prio_swap_sds", frozenset({s1_id_str, s2_id_str}), str(new_s1_assign.room_id), new_s1_assign.start_time.isoformat(), str(new_s2_assign.room_id), new_s2_assign.start_time.isoformat())
                    if tabu_list.is_tabu(move_attr): continue

                    temp_neighbor = list(base_schedule_for_prio_swap) + [new_s1_assign, new_s2_assign]
                    if self.feasibility_checker.is_feasible(temp_neighbor):
                        neighbors.append({"assignments": temp_neighbor, "move": move_attr})
                        logger.debug(f"Generated SDST-aware PRIO_SWAP: {s1_id_str} with {s2_id_str}")
                        # Found a swap, could break to reduce redundant checks or continue for more options
                        # For now, let's break after one successful prioritization swap for this high_asn
                        # to avoid too many similar neighbors from one high-urgency surgery.
                        # This break is for the inner loop (low_asn).
                        break
            # This break is for the outer loop (high_asn), if one prioritization was made for it.
            # if any(n['move'][0] == "prio_swap_sds" and high_asn.surgery_id in n['move'][1] for n in neighbors[-1:]): # Check if last added neighbor was for this high_asn
            #    break # This logic is a bit tricky; might be better to limit total prio_swaps generated.


        # Strategy 7: Block Scheduling (Enhanced)
        logger.debug("Generating neighbors: Strategy 7 - Block Scheduling by Surgeon")
        surgeon_to_assignments_map = {}
        for surgery_obj_iter in surgeries_in_schedule:
            s_id_str = str(getattr(surgery_obj_iter, 'id', getattr(surgery_obj_iter, 'surgery_id', None)))
            assignment_obj_iter = next((ra_obj for ra_obj in current_schedule_assignments if str(ra_obj.surgery_id) == s_id_str), None)
            if not assignment_obj_iter: continue # Skip if no assignment found for this surgery_id
            # Prefer surgeon_id from the surgery object itself, fall back to assignment if necessary (though ideally they match)
            surgeon_id_of_surgery = str(getattr(surgery_obj_iter, 'surgeon_id', getattr(assignment_obj_iter, 'surgeon_id', None)))
            if not surgeon_id_of_surgery: continue # Skip if surgeon_id cannot be determined

            if surgeon_id_of_surgery not in surgeon_to_assignments_map:
                surgeon_to_assignments_map[surgeon_id_of_surgery] = []
            surgeon_to_assignments_map[surgeon_id_of_surgery].append((surgery_obj_iter, assignment_obj_iter))

        for surgeon_id_key, assignments_for_surgeon_list in surgeon_to_assignments_map.items():
            if len(assignments_for_surgeon_list) < 2: continue
            try:
                # Sort surgeon's assignments by start time
                assignments_for_surgeon_list.sort(key=lambda x_item: datetime.fromisoformat(x_item[1]['start_time']))
                for i_idx in range(len(assignments_for_surgeon_list) - 1):
                    surgery1_obj, assignment1_dict = assignments_for_surgeon_list[i_idx]
                    surgery2_obj, assignment2_dict = assignments_for_surgeon_list[i_idx+1]
                    s1_id_str = str(getattr(surgery1_obj, 'id', getattr(surgery1_obj, 'surgery_id', None)))
                    s2_id_str = str(getattr(surgery2_obj, 'id', getattr(surgery2_obj, 'surgery_id', None)))

                    end1_dt = datetime.fromisoformat(assignment1_dict['end_time'])
                    start2_dt = datetime.fromisoformat(assignment2_dict['start_time'])
                    # Try to close gap if in different rooms or same room with significant gap
                    gap_seconds = (start2_dt - end1_dt).total_seconds()
                    min_gap_seconds = 15 * 60 # 15 minutes buffer

                    if str(assignment1_dict.get('room_id')) != str(assignment2_dict.get('room_id')) or gap_seconds > min_gap_seconds + 60: # If different rooms or gap > 15+1 min
                        move_representation = f"block_schedule_{s2_id_str}_after_{s1_id_str}_for_surgeon_{surgeon_id_key}"
                        if tabu_list.is_tabu(move_representation): continue

                        neighbor_assignments_block_list = copy.deepcopy(current_schedule_assignments)
                        assignment2_copy_dict = next((na_dict for na_dict in neighbor_assignments_block_list if str(na_dict.get('surgery_id')) == s2_id_str), None)
                        if not assignment2_copy_dict: continue

                        # SDST-aware block scheduling: Try to move surgery2 to the same room as surgery1, right after it
                        target_room_id_for_s2 = assignment1_dict.get('room_id')
                        s2_type_id = self._get_surgery_type_id(s2_id_str)
                        s2_duration_minutes = (datetime.fromisoformat(assignment2_dict['end_time']) - datetime.fromisoformat(assignment2_dict['start_time'])).total_seconds() / 60

                        # Base schedule for finding slot for s2, excluding s2 itself
                        base_schedule_for_s2_block = [a for a in current_schedule_assignments if str(a.surgery_id) != s2_id_str]

                        # The surgery preceding s2 in its new slot will be s1
                        last_surgery_type_in_target_room_before_s2 = self._get_surgery_type_id(s1_id_str)

                        # Attempt to schedule s2 right after s1 in s1's room
                        # We use s1's end time as the earliest_start_time for s2
                        # The find_next_available_time will add the SDST based on s1_type and s2_type
                        found_slot_for_s2 = self.scheduler_utils.find_next_available_time(
                            room_id=target_room_id_for_s2,
                            earliest_start_time=end1_dt, # s1's end time
                            duration_minutes=int(s2_duration_minutes),
                            current_assignments=base_schedule_for_s2_block,
                            surgery_id_to_schedule=s2_id_str, # For logging/debugging in find_next_available_time
                            last_surgery_type_in_room=last_surgery_type_in_target_room_before_s2,
                            current_surgery_type=s2_type_id
                        )

                        if not found_slot_for_s2:
                            logger.debug(f"Block Scheduling: No SDST-aware slot found for {s2_id_str} after {s1_id_str} in room {target_room_id_for_s2}.")
                            continue

                        new_start2_dt = found_slot_for_s2['start_time']
                        new_end2_dt = found_slot_for_s2['end_time']

                        # Update the assignment for s2 in the copied neighbor schedule
                        # Find the actual object to update in neighbor_assignments_block_list
                        actual_assignment2_to_update = next((na for na in neighbor_assignments_block_list if str(na.surgery_id) == s2_id_str), None)
                        if not actual_assignment2_to_update: continue # Should not happen if copy was correct

                        actual_assignment2_to_update.room_id = target_room_id_for_s2
                        actual_assignment2_to_update.start_time = new_start2_dt
                        actual_assignment2_to_update.end_time = new_end2_dt
                        # Surgeon ID remains the same for block scheduling by surgeon


                        if self.feasibility_checker.is_feasible(neighbor_assignments_block_list):
                            neighbors.append({"assignments": neighbor_assignments_block_list, "move": move_representation})
            except Exception as e:
                logger.error(f"Error in block scheduling for surgeon {surgeon_id_key}: {e}")

        logger.info(f"Generated {len(neighbors)} neighbor solutions.")
        return neighbors