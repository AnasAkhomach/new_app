from datetime import datetime
# Utility calculators are assumed to be refactored for SQLAlchemy or to work with passed data
from utils.equipment_utilization_calculator import EquipmentUtilizationCalculator
from utils.operational_cost_calculator import OperationalCostCalculator
from utils.room_utilization_calculator import RoomUtilizationCalculator
from utils.workload_balance_calculator import WorkloadBalanceCalculator
from utils.preference_satisfaction_calculator import PreferenceSatisfactionCalculator
from utils.resource_utilization_efficiency_calculator import ResourceUtilizationEfficiencyCalculator
from utils.equipment_utilization_efficiency_calculator import EquipmentUtilizationEfficiencyCalculator

# scheduling_utils.py was MongoDB-dependent and has been removed.
# Placeholder/simplified logic or direct implementation will be used if its functionality is critical.

class Solution:
    def __init__(self, db_session=None):
        self.db_session = db_session # SQLAlchemy session

        # Data attributes, to be populated via db_session or passed directly
        self.surgeries = []
        self.rooms = {} # room_id: room_object
        self.equipment = {} # equipment_id: equipment_object
        self.surgeons = []
        self.room_assignments = []

        self.initialize_calculators()

        self.start_date = None
        self.end_date = None
        self.score = 0
        # Metrics attributes
        self.workload_balance = None
        self.preference_satisfaction = None
        self.resource_utilization_efficiency = None
        self.surgeon_schedule_compactness = None
        self.equipment_utilization_efficiency = None
        self.operational_cost_minimization = None
        self.room_utilization_efficiency = None

    def set_analysis_period(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def fetch_initial_data(self):
        print("fetch_initial_data: Placeholder for fetching data using SQLAlchemy session.")
        if self.db_session:
            # Example: self.surgeries = self.db_session.query(SurgeryModel).all()
            # self.rooms = {room.room_id: room for room in self.db_session.query(RoomModel).all()}
            # ... and so on for other data attributes
            pass
        else:
            print("fetch_initial_data: No db_session provided. Using empty/default data.")

    def initialize_calculators(self):
        # Pass db_session to calculators if they need it, or ensure they work with data passed to their methods
        self.workload_balance_calculator = WorkloadBalanceCalculator(db_session=self.db_session)
        self.preference_satisfaction_calculator = PreferenceSatisfactionCalculator(db_session=self.db_session)
        self.equipment_utilization_calculator = EquipmentUtilizationCalculator(db_session=self.db_session)
        self.operational_cost_calculator = OperationalCostCalculator(db_session=self.db_session)
        self.room_utilization_calculator = RoomUtilizationCalculator(db_session=self.db_session)
        self.resource_utilization_efficiency_calculator = ResourceUtilizationEfficiencyCalculator(db_session=self.db_session)
        self.equipment_utilization_efficiency_calculator = EquipmentUtilizationEfficiencyCalculator(db_session=self.db_session)
        print("Calculators initialized.")

    def calculate_score(self):
        # Ensure all metrics are calculated before scoring
        if any(m is None for m in [self.workload_balance, self.preference_satisfaction,
                                   self.resource_utilization_efficiency, self.equipment_utilization_efficiency,
                                   self.surgeon_schedule_compactness, self.operational_cost_minimization,
                                   self.room_utilization_efficiency]):
            print("Warning: Not all metrics calculated. Score may be incomplete.")
            # Fallback to zero or re-calculate if necessary
            self.calculate_all_metrics() # Attempt to calculate them if not done

        # Example weights (these should be class attributes or configurable)
        weight_workload_balance = 2.0
        weight_preference_satisfaction = 1.5
        weight_resource_utilization_efficiency = 2.0
        weight_equipment_utilization_efficiency = 1.0
        weight_surgeon_schedule_compactness = 1.5
        weight_operational_cost_minimization = 2.5
        weight_room_utilization_efficiency = 2.0

        self.score = (
            (self.workload_balance or 0) * weight_workload_balance +
            (self.preference_satisfaction or 0) * weight_preference_satisfaction +
            (self.resource_utilization_efficiency or 0) * weight_resource_utilization_efficiency +
            (self.equipment_utilization_efficiency or 0) * weight_equipment_utilization_efficiency +
            (self.surgeon_schedule_compactness or 0) * weight_surgeon_schedule_compactness +
            (self.operational_cost_minimization or 0) * weight_operational_cost_minimization +
            (self.room_utilization_efficiency or 0) * weight_room_utilization_efficiency
        )
        print(f"Overall solution score: {self.score}")
        return self.score

    def update_metrics(self):
        """Recalculates all metrics and the overall score."""
        self.calculate_all_metrics()
        self.calculate_score()
        print("Metrics and score updated.")

    # Individual metric calculation methods
    def _calculate_workload_balance(self):
        try:
            # Assuming surgeries data is in self.surgeries
            self.workload_balance = self.workload_balance_calculator.calculate_workload_balance(self.surgeries)
        except Exception as e:
            print(f"Error calculating workload balance: {e}")
            self.workload_balance = 0 # Default to 0 on error

    def _calculate_preference_satisfaction(self):
        try:
            # Assuming surgeries data and surgeon_preferences_map are available or fetched
            # This might require fetching surgeon preferences if not already loaded
            surgeon_preferences_map = self._get_all_surgeon_preferences() # Helper to get map
            self.preference_satisfaction = self.preference_satisfaction_calculator.calculate(self.surgeries, surgeon_preferences_map)
        except Exception as e:
            print(f"Error calculating preference satisfaction: {e}")
            self.preference_satisfaction = 0

    def _calculate_equipment_utilization_efficiency(self):
        try:
            # Requires self.surgeries and self.equipment data
            self.equipment_utilization_efficiency = self.equipment_utilization_efficiency_calculator.calculate(
                surgeries_data=self.surgeries, equipments_data=list(self.equipment.values()),
                start_date=self.start_date, end_date=self.end_date
            )
        except Exception as e:
            print(f"Error calculating equipment utilization efficiency: {e}")
            self.equipment_utilization_efficiency = 0

    def _calculate_operational_cost_minimization(self):
        try:
            self.operational_cost_minimization = self.operational_cost_calculator.calculate_average_duration(self.surgeries)
        except Exception as e:
            print(f"Error calculating operational cost: {e}")
            self.operational_cost_minimization = float('inf') # Higher is worse

    def _calculate_room_utilization_efficiency(self):
        try:
            # Requires self.room_assignments data
            self.room_utilization_efficiency = self.room_utilization_calculator.calculate(
                room_assignments_data=self.room_assignments,
                start_date=self.start_date, end_date=self.end_date
            )
        except Exception as e:
            print(f"Error calculating room utilization efficiency: {e}")
            self.room_utilization_efficiency = 0

    def _calculate_resource_utilization_efficiency(self):
        try:
            self.resource_utilization_efficiency = self.resource_utilization_efficiency_calculator.calculate(
                surgeries_data=self.surgeries,
                start_date=self.start_date,
                end_date=self.end_date
            )
        except Exception as e:
            print(f"Error calculating resource utilization efficiency: {e}")
            self.resource_utilization_efficiency = 0

    def _calculate_surgeon_schedule_compactness(self):
        surgeon_schedules = {}
        compactness_scores = []
        try:
            for surgery in self.surgeries:
                surgeon_id = getattr(surgery, 'surgeon_id', None)
                start_time_str = getattr(surgery, 'start_time', None)
                end_time_str = getattr(surgery, 'end_time', None)

                if not all([surgeon_id, start_time_str, end_time_str]):
                    continue

                # Ensure times are datetime objects
                start_time = datetime.fromisoformat(start_time_str) if isinstance(start_time_str, str) else start_time_str
                end_time = datetime.fromisoformat(end_time_str) if isinstance(end_time_str, str) else end_time_str

                if surgeon_id not in surgeon_schedules:
                    surgeon_schedules[surgeon_id] = []
                surgeon_schedules[surgeon_id].append((start_time, end_time))

            for surgeon_id, times in surgeon_schedules.items():
                times.sort(key=lambda x: x[0])  # Sort surgeries by start time
                gaps = [(times[i][0] - times[i-1][1]).total_seconds() / 3600
                        for i in range(1, len(times)) if times[i][0] > times[i-1][1]]
                total_gap_hours = sum(gaps)
                # Compactness: Higher is better. Inverse of (1 + total_gap_hours)
                compactness = 1 / (1 + total_gap_hours) if total_gap_hours >= 0 else 1
                compactness_scores.append(compactness)

            overall_compactness = sum(compactness_scores) / len(compactness_scores) if compactness_scores else 0
            self.surgeon_schedule_compactness = overall_compactness
        except Exception as e:
            print(f"Error calculating surgeon schedule compactness: {e}")
            self.surgeon_schedule_compactness = 0

    def calculate_all_metrics(self):
        print("Calculating all metrics...")
        if not self.start_date or not self.end_date:
            print("Warning: Analysis period (start_date, end_date) not set. Metrics might be inaccurate.")

        # Fetch data if not already populated and db_session is available
        if not self.surgeries and self.db_session: # Basic check, might need more robust logic
            self.fetch_initial_data()

        self._calculate_workload_balance()
        self._calculate_preference_satisfaction()
        self._calculate_resource_utilization_efficiency()
        self._calculate_equipment_utilization_efficiency()
        self._calculate_operational_cost_minimization()
        self._calculate_room_utilization_efficiency()
        self._calculate_surgeon_schedule_compactness()

        print("Workload Balance:", self.workload_balance)
        print("Preference Satisfaction:", self.preference_satisfaction)
        print("Resource Utilization Efficiency:", self.resource_utilization_efficiency)
        print("Equipment Utilization Efficiency:", self.equipment_utilization_efficiency)
        print("Operational Cost Minimization (Avg Duration):", self.operational_cost_minimization)
        print("Room Utilization Efficiency:", self.room_utilization_efficiency)
        print("Surgeon Schedule Compactness:", self.surgeon_schedule_compactness)

    def _get_all_surgeon_preferences(self):
        """Helper to fetch/construct surgeon preferences map."""
        prefs_map = {}
        if self.db_session:
            # Placeholder: Query SurgeonPreferenceModel
            # for surgeon in self.surgeons:
            #     pref = self.db_session.query(SurgeonPreferenceModel).filter_by(surgeon_id=surgeon.id).first()
            #     prefs_map[surgeon.id] = pref.preferences if pref else {}
            print("_get_all_surgeon_preferences: DB query not implemented.")
            # Fallback for now if surgeons list is populated manually
            for surgeon in self.surgeries: # Assuming surgeons are in self.surgeries for now
                 if hasattr(surgeon, 'surgeon_id') and hasattr(surgeon, 'preferences'):
                    prefs_map[surgeon.surgeon_id] = getattr(surgeon, 'preferences', {})
        else: # No DB session, try to use manually populated self.surgeons if available
             for surgeon in self.surgeons: # self.surgeons should be list of Surgeon objects
                 if hasattr(surgeon, 'staff_id') and hasattr(surgeon, 'preferences'): # Check attributes of Surgeon model
                    prefs_map[surgeon.staff_id] = getattr(surgeon, 'preferences', {})
        return prefs_map

    def get_surgeon_preferences(self, surgeon_id):
        print(f"get_surgeon_preferences for {surgeon_id}: Placeholder for SQLAlchemy.")
        if self.db_session:
            # Example: preference = self.db_session.query(SurgeonPreferenceModel).filter_by(surgeon_id=surgeon_id).first()
            # return preference.preferences if preference else {}
            pass
        return {}

    def check_time_slot(self, surgery_id, proposed_start, proposed_end):
        print(f"check_time_slot for surgery {surgery_id}: Placeholder logic.")
        # This method would involve checking surgeon, room, and equipment availability
        # using self.db_session for queries or in-memory data if db_session is not used.
        # Example for surgeon availability (conceptual):
        # surgery_details = self.db_session.query(SurgeryModel).get(surgery_id)
        # if not is_surgeon_available(self.db_session, surgery_details.surgeon_id, proposed_start, proposed_end):
        #     return False
        return True # Placeholder: always available

    def get_dynamic_room_availability(self):
        room_availability = {}
        if self.db_session:
            # Placeholder: rooms_data = self.db_session.query(RoomModel).all()
            print("get_dynamic_room_availability: DB query for rooms not implemented.")
            rooms_data = list(self.rooms.values()) # Fallback to in-memory if populated
        else:
            rooms_data = list(self.rooms.values())

        for room in rooms_data: # Assuming room is an object with attributes
            room_id = getattr(room, 'room_id', None)
            if not room_id: continue

            default_hours = getattr(room, 'default_available_hours', 0)
            maintenance_periods = getattr(room, 'maintenance_periods', [])

            maintenance_deduction = 0
            for maint in maintenance_periods:
                # Assuming maint is a dict {'start': datetime, 'end': datetime}
                m_start, m_end = maint.get('start'), maint.get('end')
                if m_start and m_end and isinstance(m_start, datetime) and isinstance(m_end, datetime):
                    maintenance_deduction += (m_end - m_start).total_seconds() / 3600

            room_availability[room_id] = max(0, default_hours - maintenance_deduction)
        return room_availability

# Main execution / example usage
if __name__ == '__main__':
    print("Running Solution example...")
    # Conceptual: Initialize with a SQLAlchemy session if using a database
    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker
    # SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://user:pass@host/db"
    # engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # db_session_instance = SessionLocal()
    # solution_instance = Solution(db_session=db_session_instance)

    # For demonstration without a live DB session:
    solution_instance = Solution()

    # Set analysis period
    solution_instance.set_analysis_period(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31)
    )

    # Populate with some mock data if not using DB
    # This would typically come from fetch_initial_data() if db_session was real
    from models import Surgery # Assuming Surgery model exists
    solution_instance.surgeries = [
        Surgery(surgery_id='S001', surgeon_id='DR01', duration=120, start_time='2023-10-10T09:00:00', end_time='2023-10-10T11:00:00', room_id='R1', preferences={'day_off': 'Monday'}),
        Surgery(surgery_id='S002', surgeon_id='DR02', duration=90, start_time='2023-10-10T11:30:00', end_time='2023-10-10T13:00:00', room_id='R2', preferences={}),
        Surgery(surgery_id='S003', surgeon_id='DR01', duration=150, start_time='2023-10-11T14:00:00', end_time='2023-10-11T16:30:00', room_id='R1', preferences={})
    ]
    # Populate other data like self.rooms, self.equipment, self.surgeons, self.room_assignments similarly for full testing
    from models import OperatingRoom
    solution_instance.rooms = {
        'R1': OperatingRoom(room_id='R1', name='Room 1', default_available_hours=8*5, maintenance_periods=[]),
        'R2': OperatingRoom(room_id='R2', name='Room 2', default_available_hours=8*5, maintenance_periods=[])
    }
    solution_instance.room_assignments = [
        {'surgery_id': 'S001', 'room_id': 'R1', 'start_time': '2023-10-10T09:00:00', 'end_time': '2023-10-10T11:00:00'},
        {'surgery_id': 'S002', 'room_id': 'R2', 'start_time': '2023-10-10T11:30:00', 'end_time': '2023-10-10T13:00:00'},
        {'surgery_id': 'S003', 'room_id': 'R1', 'start_time': '2023-10-11T14:00:00', 'end_time': '2023-10-11T16:30:00'}
    ]

    # Calculate all metrics
    solution_instance.calculate_all_metrics()

    # Calculate overall score
    final_score = solution_instance.calculate_score()
    print(f"Final Solution Score: {final_score}")

    # if db_session_instance: db_session_instance.close()
