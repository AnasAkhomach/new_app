# This file will contain the logic for generating neighborhood solutions.
import random
import copy # For deep copying solutions
import logging
from datetime import datetime, timedelta
from models import SurgeryRoomAssignment # Assuming models.py is accessible

logger = logging.getLogger(__name__)

class NeighborhoodStrategies:
    def __init__(self, db_session, surgeries_data, operating_rooms_data, surgeons_data, feasibility_checker, scheduler_utils):
        self.db_session = db_session
        self.surgeries_data = surgeries_data # List of Surgery objects/data
        self.operating_rooms_data = operating_rooms_data # List of OR objects/data
        self.surgeons_data = surgeons_data # List of Surgeon objects/data
        self.feasibility_checker = feasibility_checker # Instance of FeasibilityChecker
        self.scheduler_utils = scheduler_utils # Instance of SchedulerUtils
        logger.info("NeighborhoodStrategies initialized.")

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

        # Strategy 1: Move Surgery to a Different Room
        logger.debug("Generating neighbors: Strategy 1 - Move Surgery to a Different Room")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(surgery_obj.id if hasattr(surgery_obj, 'id') else getattr(surgery_obj, 'surgery_id', None))
            current_assignment_obj = next((
                asn_obj for asn_obj in current_schedule_assignments if hasattr(asn_obj, 'surgery_id') and str(asn_obj.surgery_id) == surgery_id_str
            ), None)
            if not current_assignment_obj: continue

            current_room_id = str(current_assignment_obj.room_id if hasattr(current_assignment_obj, 'room_id') else None)
            possible_rooms = [r for r in self.operating_rooms_data if hasattr(r, 'id') and str(r.id) != current_room_id]
            random.shuffle(possible_rooms)

            for room_obj in possible_rooms[:min(len(possible_rooms), 3)]:
                room_id_str = str(room_obj.id if hasattr(room_obj, 'id') else None)
                move = (surgery_id_str, room_id_str, "move_to_room")
                if tabu_list.is_tabu(move): continue

                surgery_duration_minutes = surgery_obj.duration_minutes if hasattr(surgery_obj, 'duration_minutes') else getattr(surgery_obj, 'duration', 120)

                try:
                    original_start_dt = current_assignment_obj.start_time # Already datetime object
                    if not isinstance(original_start_dt, datetime):
                        logger.warning(f"start_time for surgery {surgery_id_str} is not a datetime object: {type(original_start_dt)}")
                        # Fallback or skip logic might be needed here if original_start_dt is not datetime
                        search_start_for_new_room = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    else:
                        search_start_for_new_room = original_start_dt.replace(hour=8, minute=0, second=0, microsecond=0)
                except AttributeError:
                    logger.warning(f"current_assignment_obj for surgery {surgery_id_str} missing start_time. Using default search start.")
                    search_start_for_new_room = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)

                # Attempt to find a slot using scheduler_utils.find_next_available_time
                # This is a conceptual call. The actual find_next_available_time might need different params.
                # For now, we'll construct a potential start/end time and check feasibility.
                # This part is highly dependent on how find_next_available_time is implemented.
                # Let's use a simplified approach: try to place it at a common start time if possible.
                potential_start_time_dt = search_start_for_new_room # Placeholder
                # A more robust way: self.scheduler_utils.find_next_available_time for room_id_str, surgery_duration_minutes, etc.
                # For now, let's just try a fixed time for simplicity in this refactoring step.
                # This is a significant simplification and would need to be addressed.
                potential_start_time_str = potential_start_time_dt.isoformat()
                potential_end_time_str = (potential_start_time_dt + timedelta(minutes=surgery_duration_minutes)).isoformat()

                # Create a SurgeryRoomAssignment model instance for the new assignment
                new_assignment_obj = SurgeryRoomAssignment(
                    surgery_id=int(surgery_id_str) if surgery_id_str and surgery_id_str.isdigit() else None,
                    room_id=int(room_id_str) if room_id_str and room_id_str.isdigit() else None,
                    start_time=potential_start_time_dt, # This should be a datetime object
                    end_time=(potential_start_time_dt + timedelta(minutes=surgery_duration_minutes)), # This should be a datetime object
                    surgeon_id=int(surgery_obj.surgeon_id) if hasattr(surgery_obj, 'surgeon_id') and surgery_obj.surgeon_id and str(surgery_obj.surgeon_id).isdigit() else None
                )

                neighbor_assignments_list = [asn for asn in current_schedule_assignments if hasattr(asn, 'surgery_id') and str(asn.surgery_id) != surgery_id_str]
                neighbor_assignments_list.append(new_assignment_obj)

                if self.feasibility_checker.is_feasible(neighbor_assignments_list):
                    neighbors.append({"assignments": neighbor_assignments_list, "move": move})
                else:
                    logger.debug(f"Move neighbor for surgery {surgery_id_str} to room {room_id_str} (slot: {potential_start_time_str}) resulted in infeasible schedule.")

        # Strategy 2: Swap Two Surgeries
        logger.debug("Generating neighbors: Strategy 2 - Swap Two Surgeries")
        if len(current_schedule_assignments) >= 2:
            num_swap_attempts = min(len(current_schedule_assignments) * (len(current_schedule_assignments) - 1) // 2, 10)
            for _ in range(num_swap_attempts):
                if len(current_schedule_assignments) < 2: break
                try:
                    idx1, idx2 = random.sample(range(len(current_schedule_assignments)), 2)
                except ValueError:
                    continue # Not enough items to sample
                assignment1_obj = current_schedule_assignments[idx1]
                assignment2_obj = current_schedule_assignments[idx2]

                if not (hasattr(assignment1_obj, 'surgery_id') and hasattr(assignment2_obj, 'surgery_id')):
                    continue

                surgery1_id_str = str(assignment1_obj.surgery_id)
                surgery2_id_str = str(assignment2_obj.surgery_id)

                tabu_swap_representation = tuple(sorted((f"swap_{surgery1_id_str}", f"swap_{surgery2_id_str}")))
                if tabu_list.is_tabu(tabu_swap_representation): continue

                neighbor_assignments_swap_list = copy.deepcopy(current_schedule_assignments)
                temp_assign1_ref_obj = next((na for na in neighbor_assignments_swap_list if hasattr(na, 'surgery_id') and str(na.surgery_id) == surgery1_id_str), None)
                temp_assign2_ref_obj = next((na for na in neighbor_assignments_swap_list if hasattr(na, 'surgery_id') and str(na.surgery_id) == surgery2_id_str), None)

                if not temp_assign1_ref_obj or not temp_assign2_ref_obj: continue

                if not all(hasattr(obj, attr) for obj in [temp_assign1_ref_obj, temp_assign2_ref_obj] for attr in ['room_id', 'start_time', 'end_time']):
                    logger.warning(f"Skipping swap for {surgery1_id_str} and {surgery2_id_str} due to missing attributes.")
                    continue

                room1, start1, end1 = temp_assign1_ref_obj.room_id, temp_assign1_ref_obj.start_time, temp_assign1_ref_obj.end_time
                temp_assign1_ref_obj.room_id, temp_assign1_ref_obj.start_time, temp_assign1_ref_obj.end_time = \
                    temp_assign2_ref_obj.room_id, temp_assign2_ref_obj.start_time, temp_assign2_ref_obj.end_time
                temp_assign2_ref_obj.room_id, temp_assign2_ref_obj.start_time, temp_assign2_ref_obj.end_time = room1, start1, end1

                if self.feasibility_checker.is_feasible(neighbor_assignments_swap_list):
                    neighbors.append({"assignments": neighbor_assignments_swap_list, "move": tabu_swap_representation})
                else:
                    logger.debug(f"Swap neighbor (surgeries {surgery1_id_str}, {surgery2_id_str}) resulted in infeasible schedule.")

        # Strategy 3: Shift Surgery Time within the same room
        logger.debug("Generating neighbors: Strategy 3 - Shift Surgery Time")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(surgery_obj.id if hasattr(surgery_obj, 'id') else getattr(surgery_obj, 'surgery_id', None))
            current_assignment_obj = next((asn_obj for asn_obj in current_schedule_assignments if hasattr(asn_obj, 'surgery_id') and str(asn_obj.surgery_id) == surgery_id_str), None)
            if not current_assignment_obj: continue

            if not all(hasattr(current_assignment_obj, attr) for attr in ['start_time', 'end_time', 'room_id']):
                logger.warning(f"Skipping shift for surgery {surgery_id_str} due to missing attributes in its assignment.")
                continue

            time_deltas_minutes = [-60, -45, -30, -15, 15, 30, 45, 60]
            random.shuffle(time_deltas_minutes)

            for delta_minutes in time_deltas_minutes[:3]:
                try:
                    original_start_dt = current_assignment_obj.start_time # Already datetime
                    original_end_dt = current_assignment_obj.end_time   # Already datetime
                    if not (isinstance(original_start_dt, datetime) and isinstance(original_end_dt, datetime)):
                        logger.warning(f"Invalid datetime objects for surgery {surgery_id_str} in shift strategy.")
                        continue

                    surgery_duration_seconds = (original_end_dt - original_start_dt).total_seconds()
                    new_start_dt = original_start_dt + timedelta(minutes=delta_minutes)
                    new_end_dt = new_start_dt + timedelta(seconds=surgery_duration_seconds)

                    from datetime import time as dt_time # For time comparison
                    if not (dt_time(7,0) <= new_start_dt.time() <= dt_time(19,0) and dt_time(7,0) <= new_end_dt.time() <= dt_time(19,0)):
                        continue # Assuming operating hours 7 AM to 7 PM

                    move_representation = f"shift_{surgery_id_str}_by_{delta_minutes}mins_in_room_{current_assignment_obj.room_id}"
                    if tabu_list.is_tabu(move_representation): continue

                    neighbor_assignments_shift_list = copy.deepcopy(current_schedule_assignments)
                    assignment_to_shift_obj = next((na_obj for na_obj in neighbor_assignments_shift_list if hasattr(na_obj, 'surgery_id') and str(na_obj.surgery_id) == surgery_id_str), None)
                    if not assignment_to_shift_obj: continue

                    assignment_to_shift_obj.start_time = new_start_dt
                    assignment_to_shift_obj.end_time = new_end_dt

                    if self.feasibility_checker.is_feasible(neighbor_assignments_shift_list):
                        neighbors.append({"assignments": neighbor_assignments_shift_list, "move": move_representation})
                except Exception as e:
                    logger.error(f"Error generating shift neighbor for surgery {surgery_id_str}: {e}")

        # Strategy 4: Change Surgeon
        logger.debug("Generating neighbors: Strategy 4 - Change Surgeon")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(surgery_obj.id if hasattr(surgery_obj, 'id') else getattr(surgery_obj, 'surgery_id', None))
            current_assignment_obj = next((asn_obj for asn_obj in current_schedule_assignments if hasattr(asn_obj, 'surgery_id') and str(asn_obj.surgery_id) == surgery_id_str), None)
            if not current_assignment_obj: continue
            if not self.surgeons_data or len(self.surgeons_data) < 2: continue

            original_surgeon_id = str(surgery_obj.surgeon_id if hasattr(surgery_obj, 'surgeon_id') else getattr(current_assignment_obj, 'surgeon_id', None))

            for surgeon_new_obj in self.surgeons_data:
                new_surgeon_id_str = str(surgeon_new_obj.id if hasattr(surgeon_new_obj, 'id') else getattr(surgeon_new_obj, 'surgeon_id', None))
                if original_surgeon_id == new_surgeon_id_str: continue

                # Basic qualification check (can be expanded)
                # if hasattr(surgery_obj, "specialization") and hasattr(surgeon_new_obj, "specialization"):
                #     if surgery_obj.specialization != surgeon_new_obj.specialization: continue

                # Check new surgeon's availability using FeasibilityChecker
                if not (hasattr(current_assignment_obj, 'start_time') and hasattr(current_assignment_obj, 'end_time') and isinstance(current_assignment_obj.start_time, datetime) and isinstance(current_assignment_obj.end_time, datetime)):
                    logger.warning(f"Skipping surgeon change for surgery {surgery_id_str} due to missing or invalid time attributes.")
                    continue

                if not self.feasibility_checker.is_surgeon_available(
                    new_surgeon_id_str,
                    current_assignment_obj.start_time.isoformat(), # is_surgeon_available expects string
                    current_assignment_obj.end_time.isoformat(),   # is_surgeon_available expects string
                    current_schedule_assignments, # Pass current assignments for context
                    current_surgery_id_to_ignore=surgery_id_str
                ):
                    continue

                move = (surgery_id_str, new_surgeon_id_str, "change_surgeon")
                if tabu_list.is_tabu(move): continue

                neighbor_assignments_change_surgeon_list = copy.deepcopy(current_schedule_assignments)
                assignment_to_update_obj = next((na_obj for na_obj in neighbor_assignments_change_surgeon_list if hasattr(na_obj, 'surgery_id') and str(na_obj.surgery_id) == surgery_id_str), None)
                if not assignment_to_update_obj: continue
                # Update the surgeon_id in the copied assignment object
                if hasattr(assignment_to_update_obj, 'surgeon_id'):
                    assignment_to_update_obj.surgeon_id = int(new_surgeon_id_str) if new_surgeon_id_str and new_surgeon_id_str.isdigit() else None
                else:
                    logger.warning(f"Object for surgery {surgery_id_str} does not have surgeon_id attribute in change_surgeon strategy.")
                    continue

                if self.feasibility_checker.is_feasible(neighbor_assignments_change_surgeon_list):
                    neighbors.append({"assignments": neighbor_assignments_change_surgeon_list, "move": move})

        # Strategy 5: Reschedule to Specific Time Slot
        logger.debug("Generating neighbors: Strategy 5 - Reschedule to Specific Time Slot")
        for surgery_obj in sampled_surgeries_for_strategies:
            surgery_id_str = str(getattr(surgery_obj, 'id', getattr(surgery_obj, 'surgery_id', None)))
            current_assignment_obj = next((ra_obj for ra_obj in current_schedule_assignments if str(ra_obj.surgery_id) == surgery_id_str), None)
            if not current_assignment_obj: continue
            try:
                current_start_dt = current_assignment_obj.start_time
                current_end_dt = current_assignment_obj.end_time
                if not isinstance(current_start_dt, datetime) or not isinstance(current_end_dt, datetime):
                    logger.error(f"Skipping surgery {surgery_id_str} due to invalid start/end time types in reschedule strategy.")
                    continue
                surgery_duration_minutes = int((current_end_dt - current_start_dt).total_seconds() / 60)
                time_slots = [
                    {"name": "early_morning", "hour": 7, "minute": 30},
                    {"name": "morning", "hour": 9, "minute": 0},
                    {"name": "late_morning", "hour": 10, "minute": 30},
                    {"name": "early_afternoon", "hour": 13, "minute": 0},
                    {"name": "afternoon", "hour": 14, "minute": 30},
                    {"name": "late_afternoon", "hour": 16, "minute": 0},
                ]
                current_date = current_start_dt.date()
                for slot in time_slots:
                    slot_start_dt = datetime.combine(current_date, datetime.min.time().replace(hour=slot["hour"], minute=slot["minute"]))
                    if abs((slot_start_dt - current_start_dt).total_seconds()) < 1800: continue # Avoid rescheduling to very similar time
                    slot_end_dt = slot_start_dt + timedelta(minutes=surgery_duration_minutes)
                    from datetime import time as dt_time
                    if not (dt_time(7,0) <= slot_start_dt.time() <= dt_time(19,0) and dt_time(7,0) <= slot_end_dt.time() <= dt_time(19,0)):
                        continue
                    move_representation = f"reschedule_{surgery_id_str}_to_{slot['name']}_slot_in_room_{current_assignment_dict.get('room_id')}"
                    if tabu_list.is_tabu(move_representation): continue
                    neighbor_assignments_reschedule_list = copy.deepcopy(current_schedule_assignments)
                    assignment_to_reschedule_dict = next((na_dict for na_dict in neighbor_assignments_reschedule_list if str(na_dict.get('surgery_id')) == surgery_id_str), None)
                    if not assignment_to_reschedule_dict: continue
                    assignment_to_reschedule_dict['start_time'] = slot_start_dt.isoformat()
                    assignment_to_reschedule_dict['end_time'] = slot_end_dt.isoformat()
                    if self.feasibility_checker.is_feasible(neighbor_assignments_reschedule_list):
                        neighbors.append({"assignments": neighbor_assignments_reschedule_list, "move": move_representation})
            except Exception as e:
                logger.error(f"Error generating reschedule neighbor for surgery {surgery_id_str}: {e}")

        # Strategy 6: Prioritize Emergency Surgeries
        logger.debug("Generating neighbors: Strategy 6 - Prioritize Emergency Surgeries")
        high_urgency_assignments = []
        low_medium_urgency_assignments = []
        for surgery_obj_iter in surgeries_in_schedule: # Iterate over surgeries present in the current schedule
            s_id_str = str(getattr(surgery_obj_iter, 'id', getattr(surgery_obj_iter, 'surgery_id', None)))
            assignment_obj_iter = next((ra_obj for ra_obj in current_schedule_assignments if str(ra_obj.surgery_id) == s_id_str), None)
            if not assignment_obj_iter or not hasattr(surgery_obj_iter, 'urgency_level'): continue
            if getattr(surgery_obj_iter, 'urgency_level', 'Normal') == "High":
                high_urgency_assignments.append((surgery_obj_iter, assignment_obj_iter))
            elif getattr(surgery_obj_iter, 'urgency_level', 'Normal') in ["Low", "Medium"]:
                low_medium_urgency_assignments.append((surgery_obj_iter, assignment_obj_iter))

        for high_surgery_obj, high_assignment_obj in high_urgency_assignments:
            high_surgery_id_str = str(getattr(high_surgery_obj, 'id', getattr(high_surgery_obj, 'surgery_id', None)))
            try:
                high_start_dt = datetime.fromisoformat(high_assignment_dict['start_time'])
                earlier_low_medium_urgency = []
                for low_med_surgery_obj, low_med_assignment_dict in low_medium_urgency_assignments:
                    try:
                        low_med_start_dt = datetime.fromisoformat(low_med_assignment_dict['start_time'])
                        if low_med_start_dt < high_start_dt:
                            earlier_low_medium_urgency.append((low_med_surgery_obj, low_med_assignment_dict, low_med_start_dt))
                    except (ValueError, TypeError): continue
                earlier_low_medium_urgency.sort(key=lambda x: x[2])

                for low_med_surgery_obj, low_med_assignment_dict, _ in earlier_low_medium_urgency[:3]:
                    low_med_surgery_id_str = str(getattr(low_med_surgery_obj, 'id', getattr(low_med_surgery_obj, 'surgery_id', None)))
                    move_representation = f"prioritize_emergency_{high_surgery_id_str}_over_{low_med_surgery_id_str}"
                    if tabu_list.is_tabu(move_representation): continue
                    neighbor_assignments_prio_list = copy.deepcopy(current_schedule_assignments)
                    high_assign_copy_dict = next((na_dict for na_dict in neighbor_assignments_prio_list if str(na_dict.get('surgery_id')) == high_surgery_id_str), None)
                    low_assign_copy_dict = next((na_dict for na_dict in neighbor_assignments_prio_list if str(na_dict.get('surgery_id')) == low_med_surgery_id_str), None)
                    if not high_assign_copy_dict or not low_assign_copy_dict: continue

                    # Swap room and time between high and low/medium urgency surgeries
                    h_room, h_start, h_end = high_assign_copy_dict.get('room_id'), high_assign_copy_dict.get('start_time'), high_assign_copy_dict.get('end_time')
                    high_assign_copy_dict['room_id'], high_assign_copy_dict['start_time'], high_assign_copy_dict['end_time'] = \
                        low_assign_copy_dict.get('room_id'), low_assign_copy_dict.get('start_time'), low_assign_copy_dict.get('end_time')
                    low_assign_copy_dict['room_id'], low_assign_copy_dict['start_time'], low_assign_copy_dict['end_time'] = h_room, h_start, h_end

                    if self.feasibility_checker.is_feasible(neighbor_assignments_prio_list):
                        neighbors.append({"assignments": neighbor_assignments_prio_list, "move": move_representation})
            except Exception as e:
                logger.error(f"Error generating emergency prioritization neighbor for surgery {high_surgery_id_str}: {e}")

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

                        # Try to move surgery2 to the same room as surgery1, right after it
                        new_room_id_for_s2 = assignment1_dict.get('room_id')
                        new_start2_dt = end1_dt + timedelta(seconds=min_gap_seconds)
                        s2_duration_seconds = (datetime.fromisoformat(assignment2_dict['end_time']) - start2_dt).total_seconds()
                        new_end2_dt = new_start2_dt + timedelta(seconds=s2_duration_seconds)

                        assignment2_copy_dict['room_id'] = new_room_id_for_s2
                        assignment2_copy_dict['start_time'] = new_start2_dt.isoformat()
                        assignment2_copy_dict['end_time'] = new_end2_dt.isoformat()

                        if self.feasibility_checker.is_feasible(neighbor_assignments_block_list):
                            neighbors.append({"assignments": neighbor_assignments_block_list, "move": move_representation})
            except Exception as e:
                logger.error(f"Error in block scheduling for surgeon {surgeon_id_key}: {e}")

        logger.info(f"Generated {len(neighbors)} neighbor solutions.")
        return neighbors