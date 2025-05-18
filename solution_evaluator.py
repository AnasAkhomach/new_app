# solution_evaluator.py
import logging
from datetime import datetime, timedelta
from models import Surgery, OperatingRoom, SurgeryRoomAssignment, Surgeon, SurgeryType # Ensure Surgeon and SurgeryType are imported
from utils.preference_satisfaction_calculator import PreferenceSatisfactionCalculator
from utils.workload_balance_calculator import WorkloadBalanceCalculator
# Placeholder for operational cost calculator, to be created if needed
# from utils.operational_cost_calculator import OperationalCostCalculator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SolutionEvaluator:
    def __init__(self, db_session, weights=None, sds_times_data=None):
        self.db_session = db_session
        self.weights = weights if weights else self._default_weights()
        self.sds_times_data = sds_times_data if sds_times_data else {}
        self.preference_calculator = PreferenceSatisfactionCalculator(db_session=self.db_session)
        self.workload_calculator = WorkloadBalanceCalculator(db_session=self.db_session) # db_session might not be strictly needed if data is passed
        # self.cost_calculator = OperationalCostCalculator(db_session=self.db_session) # If using a cost calculator
        logging.info(f"SolutionEvaluator initialized with weights: {self.weights} and {len(self.sds_times_data)} SDST entries.")

    def _default_weights(self):
        # Default weights for various components of the objective function
        return {
            "or_utilization": 0.20,  # Maximize OR utilization
            "sds_time_penalty": -0.20, # Minimize total sequence-dependent setup time (negative weight for penalty)
            "staff_overtime_penalty": -0.10,  # Minimize staff overtime (negative weight for penalty)
            "surgeon_preference_satisfaction": 0.15, # Maximize surgeon preference satisfaction
            "workload_balance": 0.15, # Maximize workload balance (e.g., minimize std dev of workload)
            "patient_wait_time": -0.1,  # Minimize patient wait time
            "emergency_surgery_priority": 0.1,  # Prioritize emergency surgeries
            "operational_cost_penalty": -0.0, # Minimize operational costs (e.g. consumables, specific room costs) - currently zeroed out
            "feasibility_penalty": -100.0 # Large penalty for infeasible solutions
        }

    def evaluate_solution(self, current_solution_assignments, placeholder_start_time, placeholder_end_time):
        # current_solution_assignments is a list of SurgeryRoomAssignment objects
        # placeholder_start_time and placeholder_end_time define the evaluation window
        logging.debug(f"Evaluating solution with {len(current_solution_assignments)} assignments.")

        if not current_solution_assignments:
            logging.warning("Attempted to evaluate an empty solution.")
            return 0  # Or a very low score for an empty schedule

        # Basic feasibility check (can be expanded or rely on FeasibilityChecker)
        # For now, assume FeasibilityChecker has already vetted the solution if it's passed here.
        # If not, a basic check could be: is_feasible = self._check_basic_feasibility(current_solution_assignments)
        # if not is_feasible:
        #     return self.weights["feasibility_penalty"] # Apply a heavy penalty

        total_score, component_scores = self._calculate_objective_score(
            current_solution_assignments, placeholder_start_time, placeholder_end_time
        )
        logging.info(f"Solution evaluated. Total Score: {total_score:.2f}, Components: {component_scores}")
        return total_score

    def _calculate_objective_score(self, assignments, schedule_start_time, schedule_end_time):
        # assignments: list of SurgeryRoomAssignment objects
        # schedule_start_time, schedule_end_time: datetime objects for the overall schedule window

        component_scores = {
            "or_utilization": 0,
            "sds_time_penalty": 0,
            "staff_overtime_penalty": 0,
            "surgeon_preference_satisfaction": 0,
            "workload_balance": 0, # Lower is better for std_dev, so this might need inversion or negative weight
            "patient_wait_time": 0,
            "emergency_surgery_priority": 0,
            "operational_cost_penalty": 0
        }

        # 0. Calculate total SDST for the current schedule
        # This needs to be done first as it might influence other calculations or just be a direct cost.
        component_scores["sds_time_penalty"] = self._calculate_sds_cost(assignments)

        # 1. OR Utilization
        # Needs a list of all ORs to calculate total available time
        all_operating_rooms = self.db_session.query(OperatingRoom).all()
        component_scores["or_utilization"] = self._calculate_or_utilization(
            assignments, all_operating_rooms, schedule_start_time, schedule_end_time
        )

        # 2. Staff Overtime Penalty (Placeholder - needs detailed staff schedule data)
        # component_scores["staff_overtime_penalty"] = self._calculate_staff_overtime(assignments)

        # 3. Surgeon Preference Satisfaction
        # Assumes assignments contain SurgeryRoomAssignment objects, which have .surgery and .room attributes
        # The preference calculator now expects a list of SurgeryRoomAssignment objects
        component_scores["surgeon_preference_satisfaction"] = self.preference_calculator.calculate(assignments) / 100.0 # Normalize to 0-1

        # 4. Workload Balance
        # The workload calculator now expects a list of SurgeryRoomAssignment objects
        # Lower std_dev is better. We need to convert this to a score where higher is better.
        # For example, score = 1 / (1 + std_dev) or use a negative weight for std_dev.
        # If workload_calculator returns std_dev (lower is better):
        raw_workload_std_dev = self.workload_calculator.calculate_workload_balance(assignments)
        # Normalize: e.g. if max conceivable std_dev is X, then score = (X - raw_workload_std_dev) / X
        # Or simply, if weight is positive, use 1/(1+std_dev) or similar to make higher score better.
        # If weight is negative, can use raw_std_dev directly.
        # Let's assume a positive weight for "workload_balance" means we want to maximize a balance score.
        # A simple approach: if std_dev is 0 (perfect balance), score is 1. As std_dev increases, score decreases.
        # Max typical std_dev could be, e.g., avg number of surgeries. For now, using 1/(1+std_dev).
        component_scores["workload_balance"] = 1.0 / (1.0 + raw_workload_std_dev) # Higher is better

        # 5. Patient Wait Time (Simplified - actual wait time requires more data like request date)
        component_scores["patient_wait_time"] = self._calculate_avg_patient_metric(assignments, metric_type="wait_time")

        # 6. Emergency Surgery Priority
        component_scores["emergency_surgery_priority"] = self._calculate_avg_patient_metric(assignments, metric_type="emergency_priority")

        # 7. Operational Cost Penalty (Placeholder - needs cost data per room, equipment, etc.)
        # component_scores["operational_cost_penalty"] = self.cost_calculator.calculate_total_cost(assignments) # Example

        # Combine scores using weights
        total_objective_score = 0
        for component, score in component_scores.items():
            total_objective_score += self.weights.get(component, 0) * score
            logging.debug(f"Component {component}: Score = {score:.4f}, Weighted Contribution = {self.weights.get(component, 0) * score:.4f}")

        return total_objective_score, component_scores

    def _calculate_or_utilization(self, assignments, operating_rooms, schedule_start_time, schedule_end_time):
        total_scheduled_time_minutes = 0
        for assignment in assignments:
            if assignment.start_time and assignment.end_time and assignment.surgery:
                # Ensure surgery duration is correctly accessed
                duration = assignment.surgery.duration_minutes
                total_scheduled_time_minutes += duration

        total_available_time_minutes = 0
        # Assuming schedule_start_time and schedule_end_time define the operational window for ALL rooms for simplicity.
        # A more precise calculation would use individual room availability if it varies.
        operational_duration_per_day = (schedule_end_time - schedule_start_time).total_seconds() / 60
        if operational_duration_per_day <= 0:
            logging.warning("Operational duration is zero or negative. Cannot calculate OR utilization.")
            return 0 # Avoid division by zero if schedule window is invalid

        for room in operating_rooms:
            # This assumes all rooms are available for the entire schedule_end_time - schedule_start_time window.
            # TODO: Consider specific room availability schedules if they exist.
            total_available_time_minutes += operational_duration_per_day

        if total_available_time_minutes == 0:
            logging.warning("Total available OR time is zero. Cannot calculate OR utilization.")
            return 0 # Avoid division by zero

        utilization_percentage = (total_scheduled_time_minutes / total_available_time_minutes) # Already a 0-1 scale if durations are consistent
        logging.debug(f"OR Utilization: Total Scheduled Minutes = {total_scheduled_time_minutes}, Total Available Minutes = {total_available_time_minutes}, Utilization = {utilization_percentage:.2%}")
        return utilization_percentage # Return as a fraction (0.0 to 1.0)

    def _calculate_avg_patient_metric(self, assignments, metric_type="wait_time"):
        # Simplified: for 'wait_time', assumes lower is better (e.g. days waiting)
        # For 'emergency_priority', assumes higher is better (e.g. urgency score)
        # This needs actual data from Surgery object (e.g., surgery.urgency_level, surgery.request_date)
        total_metric_value = 0
        count = 0
        for assignment in assignments:
            if not assignment.surgery: continue
            surgery = assignment.surgery
            if metric_type == "wait_time":
                # Placeholder: requires surgery.request_date and assignment.start_time
                # Example: (assignment.start_time.date() - surgery.request_date).days
                # For now, let's use a proxy like 1 / (1 + surgery.duration_minutes) to show shorter surgeries are preferred for 'wait_time'
                # This is a placeholder and should be replaced with actual wait time calculation.
                # Let's assume wait_time is a score from 0 to 1, where 1 is best (shortest wait)
                # For now, let's use a dummy value or a simple proxy. If we want to minimize something, it should be inverted.
                # Let's say lower duration means less 'wait' in a queue, so 1/(1+duration) is a proxy for 'goodness'.
                # This is highly conceptual and needs real data.
                # For now, returning a neutral 0.5, assuming normalized score.
                metric_value = 0.5 # Placeholder
            elif metric_type == "emergency_priority":
                # Urgency: High (score 3), Medium (score 2), Low (score 1)
                urgency_map = {"High": 3, "Medium": 2, "Low": 1}
                # Ensure urgency_level is a string before mapping
                # Accessing surgery_type.name requires surgery.surgery_type to be populated correctly.
                # For now, we assume surgery.urgency_level is directly available.
                urgency_str = str(surgery.urgency_level) if surgery.urgency_level else "Low"
                metric_value = urgency_map.get(urgency_str, 0)
                # Normalize: if max score is 3, then metric_value / 3.0
                metric_value = metric_value / 3.0
            else:
                metric_value = 0

            total_metric_value += metric_value
            count += 1

        if count == 0: return 0
        avg_metric = total_metric_value / count
        # For wait_time, if we calculated actual days and want to minimize, this avg_metric would be used with a negative weight.
        # If we converted it to a 0-1 score where higher is better, then positive weight.
        # Current placeholder for wait_time is already 'higher is better'.
        # Current emergency_priority is 'higher is better' (0-1 normalized).
        logging.debug(f"Average Patient Metric ({metric_type}): {avg_metric:.4f}")
        return avg_metric

    # Placeholder for _calculate_staff_overtime - requires staff shift data and overtime rules
    # def _calculate_staff_overtime(self, assignments):
    #     total_overtime_hours = 0
    #     # Logic to calculate overtime based on staff assignments and shifts
    #     # This would iterate through assignments, check staff involved, their scheduled hours vs. actual work
    #     logging.debug(f"Calculated total staff overtime: {total_overtime_hours} hours.")
    #     # Return a penalty score, e.g., normalized overtime hours (higher means more penalty)
    #     # So if weight is negative, this value should be positive.
    #     return total_overtime_hours

    def _calculate_sds_cost(self, assignments: list[SurgeryRoomAssignment]):
        """Calculates the total sequence-dependent setup time for the given schedule."""
        total_sds_minutes = 0
        # Group assignments by room and sort by start time to find sequences
        assignments_by_room = {}
        for assign in assignments:
            if assign.room_id not in assignments_by_room:
                assignments_by_room[assign.room_id] = []
            assignments_by_room[assign.room_id].append(assign)

        for room_id, room_assignments in assignments_by_room.items():
            # Sort assignments in this room by start time
            room_assignments.sort(key=lambda x: x.start_time)
            last_surgery_type_id = None
            for current_assignment in room_assignments:
                if not current_assignment.surgery or not current_assignment.surgery.surgery_type_id:
                    logging.warning(f"Skipping SDST calculation for assignment due to missing surgery/type: {current_assignment.surgery_id}")
                    continue

                current_surgery_type_id = current_assignment.surgery.surgery_type_id

                if last_surgery_type_id is not None:
                    # Lookup SDST from the pre-loaded dictionary
                    sds_key = (last_surgery_type_id, current_surgery_type_id)
                    setup_time = self.sds_times_data.get(sds_key, 0)
                    total_sds_minutes += setup_time
                    logging.debug(f"Room {room_id}: SDST from type {last_surgery_type_id} to {current_surgery_type_id} = {setup_time} min")

                last_surgery_type_id = current_surgery_type_id

        logging.debug(f"Total calculated SDST for schedule: {total_sds_minutes} minutes.")
        # This value is a penalty, so a higher number is worse.
        # If the weight for "sds_time_penalty" is negative, this positive value will correctly reduce the score.
        return total_sds_minutes

    def _basic_evaluate_solution(self, current_solution_assignments, placeholder_start_time, placeholder_end_time):
        # This is a simpler evaluation, perhaps focusing only on OR utilization or a subset of factors.
        # Kept for potential use if a lightweight evaluation is needed sometimes.
        logging.debug(f"Basic evaluation for solution with {len(current_solution_assignments)} assignments.")
        if not current_solution_assignments:
            return 0

        all_operating_rooms = self.db_session.query(OperatingRoom).all()
        or_utilization_score = self._calculate_or_utilization(
            current_solution_assignments, all_operating_rooms, placeholder_start_time, placeholder_end_time
        )

        # Example: Basic score is just OR utilization
        # Or a weighted sum of a few key factors, using a simplified set of weights.
        basic_score = or_utilization_score * self.weights.get("or_utilization", 0.5) # Use default if not in main weights

        logging.info(f"Basic evaluation score: {basic_score:.2f} (based on OR Utilization: {or_utilization_score:.2%})")
        return basic_score

# Example usage (conceptual)
if __name__ == "__main__":
    # This example assumes you have a SQLAlchemy session (db_session) and mock data.
    # from db_config import SessionLocal # Your SQLAlchemy session factory
    # db_session = SessionLocal()

    # Mocking db_session and data for standalone execution:
    class MockDBSession:
        def query(self, model):
            if model == OperatingRoom:
                # Return a list of mock OperatingRoom objects
                room1 = OperatingRoom(room_id=1, location="North Wing")
                # setattr(room1, 'id', 1) # if 'id' is the primary key name used elsewhere
                room2 = OperatingRoom(room_id=2, location="South Wing")
                # setattr(room2, 'id', 2)
                return [room1, room2]
            return []

    class MockSurgeon:
        def __init__(self, surgeon_id, name="Test Surgeon"):
            self.surgeon_id = surgeon_id
            self.name = name

    class MockSurgery:
        def __init__(self, surgery_id, duration_minutes, urgency_level="Medium", surgeon_id=None):
            self.surgery_id = surgery_id
            self.duration_minutes = duration_minutes
            self.urgency_level = urgency_level
            self.surgeon_id = surgeon_id
            self.surgeon = MockSurgeon(surgeon_id=surgeon_id) if surgeon_id else None

    class MockOperatingRoom:
        def __init__(self, room_id, location="Test Room"):
            self.room_id = room_id
            self.location = location

    class MockSurgeryRoomAssignment:
        def __init__(self, surgery, room, start_time, end_time):
            self.surgery = surgery
            self.room = room
            self.start_time = start_time
            self.end_time = end_time

    mock_db_session = MockDBSession()
    evaluator = SolutionEvaluator(db_session=mock_db_session)

    # Define a schedule window
    schedule_start = datetime(2023, 1, 1, 8, 0, 0)  # 8 AM
    schedule_end = datetime(2023, 1, 1, 17, 0, 0)   # 5 PM

    # Create some mock SurgeryRoomAssignment objects
    surgery1 = MockSurgery(surgery_id="S1", duration_minutes=120, urgency_level="High", surgeon_id="DR1")
    room1 = MockOperatingRoom(room_id=1)
    assignment1_start = datetime(2023, 1, 1, 9, 0, 0)
    assignment1_end = datetime(2023, 1, 1, 11, 0, 0)
    assignment1 = MockSurgeryRoomAssignment(surgery1, room1, assignment1_start, assignment1_end)

    surgery2 = MockSurgery(surgery_id="S2", duration_minutes=90, urgency_level="Medium", surgeon_id="DR2")
    room2 = MockOperatingRoom(room_id=2)
    assignment2_start = datetime(2023, 1, 1, 10, 0, 0)
    assignment2_end = datetime(2023, 1, 1, 11, 30, 0)
    assignment2 = MockSurgeryRoomAssignment(surgery2, room2, assignment2_start, assignment2_end)

    surgery3 = MockSurgery(surgery_id="S3", duration_minutes=180, urgency_level="Low", surgeon_id="DR1")
    # room1 again, but later
    assignment3_start = datetime(2023, 1, 1, 13, 0, 0)
    assignment3_end = datetime(2023, 1, 1, 16, 0, 0)
    assignment3 = MockSurgeryRoomAssignment(surgery3, room1, assignment3_start, assignment3_end)


    mock_assignments = [assignment1, assignment2, assignment3]

    # Mock surgeon preferences (needed by PreferenceSatisfactionCalculator)
    # This part would typically involve the calculator fetching from db_session or being passed a map
    # For this example, let's assume get_surgeon_preferences in the calculator is mocked or works with this session
    class MockSurgeonPreference:
        def __init__(self, surgeon_id, preference_type, preference_value):
            self.surgeon_id = surgeon_id
            self.preference_type = preference_type
            self.preference_value = preference_value

    # Patching the db_session.query for SurgeonPreference if needed by the calculator
    original_query_method = mock_db_session.query
    def extended_mock_query(model):
        if model == SurgeonPreference:
            # dr_A prefers Monday, OR1
            # dr_B prefers Tuesday
            return [
                MockSurgeonPreference(surgeon_id="DR1", preference_type="day_of_week", preference_value=assignment1_start.strftime("%A")),
                MockSurgeonPreference(surgeon_id="DR1", preference_type="room_id", preference_value=str(room1.room_id)), # ensure type match
                MockSurgeonPreference(surgeon_id="DR2", preference_type="day_of_week", preference_value=assignment2_start.strftime("%A")),
            ]
        elif model == OperatingRoom:
             return original_query_method(model) # Call original for ORs
        return []
    mock_db_session.query = extended_mock_query


    total_score = evaluator.evaluate_solution(mock_assignments, schedule_start, schedule_end)
    print(f"\nExample Usage Total Objective Score: {total_score:.4f}")

    # basic_score = evaluator._basic_evaluate_solution(mock_assignments, schedule_start, schedule_end)
    # print(f"Example Usage Basic Score: {basic_score:.4f}")

    # if isinstance(mock_db_session, SessionLocal):
    #     mock_db_session.close()