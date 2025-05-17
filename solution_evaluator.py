# This file will contain the logic for evaluating solutions.
import logging
from datetime import datetime, timedelta
from solution import Solution # Assuming solution.py is in the same directory or accessible

logger = logging.getLogger(__name__)

class SolutionEvaluator:
    def __init__(self, db_session, surgeries_data, operating_rooms_data, feasibility_checker):
        self.db_session = db_session
        self.surgeries_data = surgeries_data # List of Surgery objects/data
        self.operating_rooms_data = operating_rooms_data # List of OR objects/data
        self.feasibility_checker = feasibility_checker # Instance of FeasibilityChecker
        logger.info("SolutionEvaluator initialized.")

    def evaluate_solution(self, schedule, schedule_start_time, schedule_end_time):
        """Evaluates a given schedule based on multiple criteria."""
        if not schedule:
            logger.warning("Attempted to evaluate an empty schedule.")
            return -float("inf")

        # First, check basic feasibility using the FeasibilityChecker
        # The schedule here is expected to be a list of assignment dicts/objects
        # that FeasibilityChecker.is_feasible can process.
        if not self.feasibility_checker.is_feasible(schedule):
            logger.warning("Evaluated schedule is not feasible. Returning -infinity.")
            return -float("inf")

        try:
            # Initialize Solution class from solution_analyser.py
            # This requires the Solution class to be adapted to take the schedule directly,
            # or for us to format the schedule as needed by the Solution class.
            # For now, assuming Solution class can be initialized with the schedule data.

            # The Solution class might expect data in a specific format (e.g., from DB models)
            # We need to ensure the 'schedule' (list of dicts) is compatible or transform it.
            # For simplicity, let's assume the Solution class can handle the schedule format or
            # we'd need to map it to the expected format (e.g., list of SurgeryRoomAssignment-like objects).

            # Mocking the Solution class usage if it's not fully integrated/available yet
            # or if it expects a full DB setup which might not be available here.
            # If Solution class is available and works with the provided schedule format:
            solution = Solution(self.db_session, self.surgeries_data, self.operating_rooms_data, schedule)

            # Set analysis period if required by Solution class
            if hasattr(solution, 'set_analysis_period'):
                solution.set_analysis_period(
                    start_date=schedule_start_time - timedelta(days=1),
                    end_date=schedule_end_time + timedelta(days=1),
                )

            # Calculate all metrics
            if hasattr(solution, 'calculate_all_metrics'): solution.calculate_all_metrics()

            # Calculate overall score from Solution class
            score = solution.calculate_score() if hasattr(solution, 'calculate_score') else 0.0
            logger.info(f"Evaluated solution with comprehensive score from Solution class: {score}")

            # Add additional metrics that might not be covered by Solution class or for fine-tuning

            # 1. Patient Waiting Time (Soft Constraint)
            WEIGHT_WAIT_TIME = 1.0
            total_wait_time_minutes = 0

            for assignment_item in schedule: # schedule is a list of SurgeryRoomAssignment instances
                surgery_id_val = assignment_item.surgery_id
                start_time_obj = assignment_item.start_time # Already a datetime object

                surgery_obj = next((
                    s for s in self.surgeries_data if str(getattr(s, 'id', getattr(s, 'surgery_id', None))) == str(surgery_id_val)
                ), None)

                if surgery_obj and start_time_obj: # Check if start_time_obj is not None
                    try:
                        scheduled_start_dt = start_time_obj # Already a datetime object
                        if hasattr(surgery_obj, "requested_date") and isinstance(surgery_obj.requested_date, datetime):
                            wait_duration = scheduled_start_dt - surgery_obj.requested_date
                            total_wait_time_minutes += (wait_duration.total_seconds() / 60)
                    except Exception as e:
                        logger.error(f"Error calculating wait time for surgery {surgery_id_val}: {e}")

            if total_wait_time_minutes > 0 and len(schedule) > 0:
                wait_time_score_contribution = max(0, 1 - (total_wait_time_minutes / (24 * 60 * len(schedule)))) * WEIGHT_WAIT_TIME
                score += wait_time_score_contribution
                logger.debug(f"Wait Time Score Component: {wait_time_score_contribution}")

            # 2. Emergency Surgery Priority
            WEIGHT_EMERGENCY_PRIORITY = 2.0
            emergency_priority_score_total = 0

            for assignment_item in schedule: # schedule is a list of SurgeryRoomAssignment instances
                surgery_id_val = assignment_item.surgery_id
                start_time_obj = assignment_item.start_time # Already a datetime object

                surgery_obj = next((
                    s for s in self.surgeries_data if str(getattr(s, 'id', getattr(s, 'surgery_id', None))) == str(surgery_id_val)
                ), None)

                if surgery_obj and hasattr(surgery_obj, "urgency_level") and start_time_obj:
                    try:
                        scheduled_start_dt = start_time_obj # Already a datetime object
                        if surgery_obj.urgency_level == "High":
                            time_from_schedule_start = (scheduled_start_dt - schedule_start_time).total_seconds() / 60
                            total_schedule_duration = (schedule_end_time - schedule_start_time).total_seconds() / 60
                            if total_schedule_duration > 0:
                                position_score = 1 - (time_from_schedule_start / total_schedule_duration)
                                emergency_priority_score_total += position_score
                    except Exception as e:
                        logger.error(f"Error calculating emergency priority for surgery {surgery_id_val}: {e}")

            emergency_priority_contribution = emergency_priority_score_total * WEIGHT_EMERGENCY_PRIORITY
            score += emergency_priority_contribution
            logger.debug(f"Emergency Priority Score Component: {emergency_priority_contribution}")

            # 3. Hard Constraint Penalty (double-check, already covered by is_feasible but as a safeguard)
            # This part is largely redundant if FeasibilityChecker.is_feasible is robust.
            # However, keeping a simplified version for direct penalty if something slips through.
            PENALTY_HARD_CONSTRAINT = -1000
            # The FeasibilityChecker.is_feasible call at the beginning should handle this.
            # If it returns True, we assume no such hard constraint violations.
            # If it returns False, score is already -inf.

            return score

        except Exception as e:
            logger.error(f"Error in comprehensive solution evaluation: {e}")
            return self._basic_evaluate_solution(schedule, schedule_start_time, schedule_end_time)

    def _basic_evaluate_solution(self, schedule, schedule_start_time, schedule_end_time):
        """
        Basic evaluation function as a fallback or for simpler scenarios.
        """
        if not schedule:
            return -float("inf")

        # Basic feasibility check (redundant if called after comprehensive eval's check)
        if not self.feasibility_checker.is_feasible(schedule):
             return -float("inf")

        score = 0.0
        WEIGHT_OR_UTILIZATION = 1.5 # Adjusted weight
        WEIGHT_OVERTIME = -1.0
        WEIGHT_EMERGENCY_PRIORITY = 2.5 # Adjusted weight

        total_or_occupied_time_minutes = 0
        # Assuming operating_rooms_data contains objects/dicts with 'id' and 'available_from'/'available_to' attributes
        # For simplicity, let's assume a standard operating day (e.g., 8 AM to 6 PM) if not specified per room.
        # This part needs to align with how OR availability is defined and accessed.

        # Calculate total possible OR time based on schedule_start_time and schedule_end_time for all rooms
        # This is a simplification. A more accurate calculation would use individual room availability.
        total_possible_or_time_minutes = 0
        for room in self.operating_rooms_data:
            # Example: Assume rooms are available for the full duration of the schedule window for simplicity
            # A more robust way would be to get actual available hours for each room.
            room_operational_start = schedule_start_time # Placeholder
            room_operational_end = schedule_end_time   # Placeholder

            # Consider actual room availability if available
            # room_op_hours_start = datetime.strptime(getattr(room, 'available_from', '08:00'), '%H:%M').time()
            # room_op_hours_end = datetime.strptime(getattr(room, 'available_to', '18:00'), '%H:%M').time()
            # room_operational_start = schedule_start_time.replace(hour=room_op_hours_start.hour, minute=room_op_hours_start.minute, second=0, microsecond=0)
            # room_operational_end = schedule_start_time.replace(hour=room_op_hours_end.hour, minute=room_op_hours_end.minute, second=0, microsecond=0)
            # if schedule_end_time.date() > schedule_start_time.date(): # Multi-day schedule
            #    room_operational_end = schedule_end_time.replace(hour=room_op_hours_end.hour, minute=room_op_hours_end.minute, second=0, microsecond=0)

            # Simplified: use the overall schedule window for each room's potential time
            duration_per_room_seconds = (schedule_end_time - schedule_start_time).total_seconds()
            if duration_per_room_seconds > 0:
                total_possible_or_time_minutes += duration_per_room_seconds / 60

        or_occupied_times = {room.id: 0 for room in self.operating_rooms_data if hasattr(room, 'id')}
        total_overtime_minutes = 0

        for assignment_item in schedule: # schedule is a list of SurgeryRoomAssignment instances
            start_dt = assignment_item.start_time # Already a datetime object
            end_dt = assignment_item.end_time     # Already a datetime object
            room_id_val = assignment_item.room_id

            try:
                # start_dt and end_dt are already datetime objects
                duration_minutes = (end_dt - start_dt).total_seconds() / 60
                if duration_minutes > 0:
                    total_or_occupied_time_minutes += duration_minutes
                    if room_id_val in or_occupied_times:
                        or_occupied_times[room_id_val] += duration_minutes

                # Simplified overtime calculation: any work beyond schedule_end_time's hour (e.g., 6 PM)
                # This needs refinement based on actual OR operating hours.
                # For now, let's assume schedule_end_time is the desired end of the workday.
                if end_dt > schedule_end_time: # Basic overtime check
                    overtime_this_surgery = (end_dt - schedule_end_time).total_seconds() / 60
                    total_overtime_minutes += overtime_this_surgery

            except Exception as e:
                logger.error(f"Error processing assignment in basic_evaluate: {e}")

        if total_possible_or_time_minutes > 0:
            utilization_score = (total_or_occupied_time_minutes / total_possible_or_time_minutes)
            score += utilization_score * WEIGHT_OR_UTILIZATION
            logger.debug(f"Basic Eval - OR Utilization Score Component: {utilization_score * WEIGHT_OR_UTILIZATION}")

        # Penalty for overtime (normalized, e.g., by total schedule duration or number of surgeries)
        if total_overtime_minutes > 0 and total_possible_or_time_minutes > 0:
            overtime_penalty_normalized = total_overtime_minutes / total_possible_or_time_minutes # Example normalization
            score += overtime_penalty_normalized * WEIGHT_OVERTIME # WEIGHT_OVERTIME is negative
            logger.debug(f"Basic Eval - Overtime Penalty Component: {overtime_penalty_normalized * WEIGHT_OVERTIME}")

        # Emergency surgery priority (simplified)
        emergency_priority_basic_score = 0
        high_urgency_surgeries_count = 0
        for assignment_item in schedule: # schedule is a list of SurgeryRoomAssignment instances
            surgery_id_val = assignment_item.surgery_id
            start_time_obj = assignment_item.start_time # Already a datetime object
            surgery_obj = next((s for s in self.surgeries_data if str(getattr(s, 'id', getattr(s, 'surgery_id', None))) == str(surgery_id_val)), None)
            if surgery_obj and hasattr(surgery_obj, "urgency_level") and surgery_obj.urgency_level == "High":
                high_urgency_surgeries_count += 1
                try:
                    scheduled_start_dt = start_time_obj # Already a datetime object
                    # Simple bonus for being scheduled (more complex timing logic omitted for basic)
                    # A more nuanced score would consider how early they are.
                    # For basic, just a fixed bonus per high urgency surgery scheduled.
                    emergency_priority_basic_score += 1 # Simple bonus
                except Exception as e:
                    logger.error(f"Error processing emergency surgery in basic_evaluate: {e}")

        if high_urgency_surgeries_count > 0:
            # Avoid division by zero if no high urgency surgeries
            # Normalize by number of high urgency surgeries to make it an average bonus
            normalized_emergency_score = emergency_priority_basic_score / high_urgency_surgeries_count if high_urgency_surgeries_count > 0 else 0
            score += normalized_emergency_score * WEIGHT_EMERGENCY_PRIORITY
            logger.debug(f"Basic Eval - Emergency Priority Score Component: {normalized_emergency_score * WEIGHT_EMERGENCY_PRIORITY}")

        logger.info(f"Basic evaluated solution score: {score}")
        return score