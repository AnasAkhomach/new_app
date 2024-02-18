from db_config import db
from datetime import datetime
from mongodb_transaction_manager import MongoDBClient  # Ensure this import matches your consolidated script name
from utils.equipment_utilization_calculator import EquipmentUtilizationCalculator
from utils.operational_cost_calculator import OperationalCostCalculator
from utils.room_utilization_calculator import RoomUtilizationCalculator
from utils.workload_balance_calculator import WorkloadBalanceCalculator
from utils.preference_satisfaction_calculator import PreferenceSatisfactionCalculator
from utils.resource_utilization_efficiency_calculator import ResourceUtilizationEfficiencyCalculator
from utils.equipment_utilization_efficiency_calculator import EquipmentUtilizationEfficiencyCalculator


from scheduling_utils import(is_surgeon_available,
                            is_equipment_available,
                            is_room_available,
                            is_staff_available)


from mongodb_transaction_manager import MongoDBClient
# Ensure you have imported all calculator classes above

class Solution:
    def __init__(self):
        # Establish a database connection
        self.db = MongoDBClient.get_db()
        
        # Fetch initial data needed for calculations
        self.fetch_initial_data()
        
        # Initialize calculator instances for different metrics
        self.initialize_calculators()

        self.start_date = None
        self.end_date = None

    def set_analysis_period(self, start_date, end_date):
        """Sets the analysis period for calculations."""
        self.start_date = start_date
        self.end_date = end_date                
        
    def fetch_initial_data(self):
        # Fetch surgeries data
        self.surgeries = list(self.db.surgeries.find({}))
        
        # Fetch rooms data and convert it into a dictionary for easy access
        self.rooms = {room['room_id']: room for room in self.db.rooms.find({})}
        
        # Fetch equipment data and convert it into a dictionary for easy access
        self.equipment = {equipment['equipment_id']: equipment for equipment in self.db.equipment.find({})}
        
        # Fetch surgeons data
        self.surgeons = list(self.db.surgeons.find({}))
        
        # Fetch room assignments data
        self.room_assignments = list(self.db.room_assignments.find({}))
  
    def initialize_calculators(self):
        # Initialize the Workload Balance Calculator
        self.workload_balance_calculator = WorkloadBalanceCalculator()
        
        # Initialize the Preference Satisfaction Calculator
        self.preference_satisfaction_calculator = PreferenceSatisfactionCalculator()
        
        # Initialize the Equipment Utilization Efficiency Calculator
        self.equipment_utilization_calculator = EquipmentUtilizationCalculator()
        
        # Initialize the Operational Cost Calculator
        self.operational_cost_calculator = OperationalCostCalculator()
        
        # Initialize the Room Utilization Efficiency Calculator
        self.room_utilization_calculator = RoomUtilizationCalculator()

        # Initialize each calculator with necessary parameters
        self.resource_utilization_efficiency_calculator = ResourceUtilizationEfficiencyCalculator()

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        efficiency = self.resource_utilization_efficiency_calculator.calculate(start_date, end_date)

        # Display the calculated efficiency
        print("Resource Utilization Efficiency:")
        for resource_id, efficiency_percent in efficiency.items():
            print(f"{resource_id}: {efficiency_percent}%")

        # Make sure this line is included for equipment utilization efficiency calculator
        self.equipment_utilization_efficiency_calculator = EquipmentUtilizationEfficiencyCalculator()

    def calculate_score(self):
        # Reset score before recalculating
        self.score = 0
        # Calculate score components
        self.score += self.calculate_workload_balance()
        self.score += self.calculate_preference_satisfaction()
        self.score += self.calculate_resource_utilization_efficiency()
        self.score += self.calculate_surgeon_schedule_compactness()
        self.score += self.calculate_equipment_utilization_efficiency()
        self.score += self.calculate_operational_cost_minimization()
        self.score += self.calculate_room_utilization_efficiency()
        return self.score

    def update_metrics(self):
        self.workload_balance = self.workload_balance_calculator.calculate_workload_balance()
        self.preference_satisfaction = self.preference_satisfaction_calculator.calculate(self.surgeries)
        self.resource_utilization_efficiency = self.resource_utilization_efficiency_calculator.calculate(self.start_date, self.end_date)
        self.equipment_utilization_efficiency = self.equipment_utilization_efficiency_calculator.calculate(self.start_date, self.end_date)
        self.room_utilization_efficiency = self.room_utilization_calculator.calculate(self.start_date, self.end_date)
        # Update the score based on the new metrics
        self.calculate_score()

    def calculate_workload_balance(self):
        """
        Calculates and updates the workload balance metric using the WorkloadBalanceCalculator.
        """
        try:
            self.workload_balance = self.workload_balance_calculator.calculate()
        except Exception as e:
            print(f"Error calculating workload balance: {e}")
            self.workload_balance = None

    def calculate_preference_satisfaction(self):
        """
        Calculates and updates the preference satisfaction metric using the PreferenceSatisfactionCalculator.
        """
        try:
            self.preference_satisfaction = self.preference_satisfaction_calculator.calculate(self.surgeries)
        except Exception as e:
            print(f"Error calculating preference satisfaction: {e}")
            self.preference_satisfaction = None

    def calculate_equipment_utilization_efficiency(self):
        """
        Calculates and updates the equipment utilization efficiency using the EquipmentUtilizationCalculator.
        """
        try:
            self.equipment_utilization_efficiency = self.equipment_utilization_calculator.calculate(self.start_date, self.end_date)
        except Exception as e:
            print(f"Error calculating equipment utilization efficiency: {e}")
            self.equipment_utilization_efficiency = None

    def calculate_operational_cost_minimization(self):
        """
        Calculates and updates the operational cost using the OperationalCostCalculator.
        """
        try:
            self.operational_cost_minimization = self.operational_cost_calculator.calculate()
        except Exception as e:
            print(f"Error calculating operational cost: {e}")
            self.operational_cost_minimization = None

    def calculate_room_utilization_efficiency(self):
        """
        Calculates and updates the room utilization efficiency using the RoomUtilizationCalculator.
        """
        try:
            self.room_utilization_efficiency = self.room_utilization_calculator.calculate(self.start_date, self.end_date)
        except Exception as e:
            print(f"Error calculating room utilization efficiency: {e}")
            self.room_utilization_efficiency = None

    def calculate_all_metrics(self):
        """Calculates and updates all metrics for the solution."""
        # Assuming self.surgeries is already populated
        self.workload_balance = self.workload_balance_calculator.calculate_workload_balance(self.surgeries)
        self.preference_satisfaction = self.preference_satisfaction_calculator.calculate(self.surgeries)
        self.resource_utilization_efficiency = self.resource_utilization_efficiency_calculator.calculate(self.start_date, self.end_date)
        self.equipment_utilization_efficiency = self.equipment_utilization_efficiency_calculator.calculate(self.start_date, self.end_date)
        self.operational_cost_minimization = self.operational_cost_calculator.calculate(self.surgeries)
        self.room_utilization_efficiency = self.room_utilization_calculator.calculate(self.start_date, self.end_date)
        self.resource_utilization_efficiency_calculator = ResourceUtilizationEfficiencyCalculator()
               
        # Update more metrics as needed

        # You might want to return the calculated metrics or print them
        # For demonstration purposes, we'll just print them here
        print(f"Workload Balance: {self.workload_balance}")
        print(f"Preference Satisfaction: {self.preference_satisfaction}")
        print(f"Resource Utilization Efficiency: {self.resource_utilization_efficiency}")
        print(f"Equipment Utilization Efficiency: {self.equipment_utilization_efficiency}")
        print(f"Operational Cost Minimization: {self.operational_cost_minimization}")
        print(f"Room Utilization Efficiency: {self.room_utilization_efficiency}")
        # Print more metrics as needed







    def get_surgeon_preferences(self, surgeon_id, db):
        """
        Retrieves a surgeon's preferences from the database, now optimized with db parameter.
        """
        try:
            preferences_document = db.surgeon_preferences.find_one({"surgeon_id": surgeon_id})
            return preferences_document.get('preferences', {}) if preferences_document else {}
        except Exception as e:
            print(f"Error fetching preferences for surgeon {surgeon_id}: {e}")
            return {}

    def check_time_slot(self, surgery_id, proposed_start, proposed_end):
        """
        Checks if a proposed time slot is available for a given surgery.

        Args:
            surgery_id (str): The ID of the surgery.
            proposed_start (datetime): The proposed start time for the surgery.
            proposed_end (datetime): The proposed end time for the surgery.

        Returns:
            bool: True if the time slot is available, False otherwise.
        """
        # Check surgeon availability
        surgery_details = self.db.surgeries.find_one({"_id": surgery_id})
        if not self.is_surgeon_available(surgery_details["surgeon_id"], proposed_start, proposed_end):
            print("Surgeon not available for the proposed time.")
            return False

        # Check room availability
        if not self.is_room_available(surgery_details["room_id"], proposed_start, proposed_end):
            print("Operating room not available for the proposed time.")
            return False

        # Check equipment availability (if required)
        if "equipment_needed" in surgery_details and not self.check_equipment_availability(surgery_id, proposed_start, proposed_end):
            print("Required equipment not available for the proposed time.")
            return False

        # Additional checks can be placed here (e.g., staff availability)

        return True
        
    def get_dynamic_room_availability(self, db):
        # Example: Fetching room availability considering dynamic factors
        room_availability = {}
        rooms = db.rooms.find({})  # Assuming a collection 'rooms' with availability details
        for room in rooms:
            # Calculate available hours considering maintenance or closures
            available_hours = room['default_available_hours']  # Base hours
            # Subtract hours based on maintenance schedules or closures
            for maintenance in room.get('maintenance_periods', []):
                start, end = maintenance['start'], maintenance['end']
                # Simplified calculation; actual logic may vary
                available_hours -= (end - start).total_seconds() / 3600
            room_availability[room['_id']] = max(0, available_hours)  # Ensure non-negative
        return room_availability
    
    def calculate_surgeon_schedule_compactness(self):
        """
        Calculates the compactness of each surgeon's schedule, aiming to minimize gaps between surgeries.
        """
        db = MongoDBClient.get_db()  # Ensure consistent database access
        surgeon_schedules = {}
        compactness_scores = []

        try:
            # Ideally, fetch surgery times and surgeon_ids directly from the database
            # For demonstration, assuming self.surgeries is already populated
            for surgery in self.surgeries:
                surgeon_id = surgery.get('surgeon_id')
                if surgeon_id not in surgeon_schedules:
                    surgeon_schedules[surgeon_id] = []
                start_time = surgery.get('start_time')
                end_time = surgery.get('end_time')
                if start_time and end_time:  # Ensure times are present
                    surgeon_schedules[surgeon_id].append((start_time, end_time))

            for surgeon_id, times in surgeon_schedules.items():
                times.sort(key=lambda x: x[0])  # Sort surgeries by start time
                gaps = [max(0, (times[i][0] - times[i-1][1]).total_seconds() / 3600) for i in range(1, len(times))]
                compactness = 1 / (1 + sum(gaps)) if gaps else 1  # Higher score for less idle time
                compactness_scores.append(compactness)

            overall_compactness = sum(compactness_scores) / len(compactness_scores) if compactness_scores else 0
            self.surgeon_schedule_compactness = overall_compactness
            return overall_compactness
        except Exception as e:
            print(f"An error occurred while calculating surgeon schedule compactness: {e}")
            self.surgeon_schedule_compactness = None
            return None

    def calculate_and_set_operational_cost(self):
        # Create an instance of the calculator with the database connection
        db = MongoDBClient.get_db()
        cost_calculator = OperationalCostCalculator(db)

        # Calculate the average surgery duration
        self.average_surgery_duration = cost_calculator.calculate_operational_cost_minimization()

        # Use the average duration as a proxy for operational cost
        # You might want to store it in the instance or use it directly
        # For example:
        self.operational_cost_minimization = self.average_surgery_duration

    def calculate_room_utilization(self):
        # Instantiate the calculator
        room_utilization_calculator = RoomUtilizationCalculator()
        
        # Define your date range for the calculation
        start_date = datetime(2023, 1, 1)  # Example start date
        end_date = datetime(2023, 12, 31)  # Example end date
        
        # Perform the calculation
        self.room_utilization_efficiency = room_utilization_calculator.calculate_room_utilization_efficiency(start_date, end_date)
        
        # Use or store the calculated efficiencies as needed
        # For example, printing them:
        print("Room Utilization Efficiency:")
        for room_id, efficiency in self.room_utilization_efficiency.items():
            print(f"Room ID: {room_id}, Utilization Efficiency: {efficiency:.2f}%")

    def calculate_operational_hours_per_room(self):
        """
        Calculates the operational hours for each room, considering various factors
        such as regular operating hours, maintenance schedules, and special closures.
        """
        operational_hours_per_room = {}
        for room in self.rooms:
            if isinstance(room, dict) and 'room_id' in room and 'operating_hours' in room:
                room_id = room['room_id']
                operating_hours = room['operating_hours']  # A dictionary with days of the week and hours, e.g., {'Monday': [8, 16]}
                maintenance_periods = room.get('maintenance_periods', [])  # List of periods when the room is unavailable
                
                # Calculate total operational hours by subtracting maintenance hours from regular operating hours
                total_operational_hours = self.calculate_weekly_operational_hours(operating_hours) - self.calculate_maintenance_downtime(maintenance_periods)
                
                operational_hours_per_room[room_id] = max(0, total_operational_hours)  # Ensure non-negative values
            else:
                print(f"Invalid room data encountered: {room}")

        return operational_hours_per_room

    def calculate_weekly_operational_hours(self, operating_hours):
        """
        Calculates the total operational hours in a week based on a room's operating hours.
        """
        total_hours = 0
        for day, hours in operating_hours.items():
            # Assuming 'hours' is a list of opening and closing times
            for start, end in hours:
                total_hours += end - start
        return total_hours

    def calculate_maintenance_downtime(self, maintenance_periods):
        """
        Calculates the total downtime due to maintenance in a given period.
        """
        total_downtime = 0
        for period in maintenance_periods:
            start, end = period['start'], period['end']
            # Assuming 'start' and 'end' are datetime objects
            downtime = (end - start).total_seconds() / 3600  # Convert seconds to hours
            total_downtime += downtime
        return total_downtime

    def calculate_used_hours_per_room(self):
        """
        Calculates the total used hours for each room based on surgeries.
        """
        total_used_hours_per_room = {}
        for surgery in self.surgeries:
            if 'room_id' in surgery and 'start_time' in surgery and 'end_time' in surgery:
                room_id = surgery['room_id']
                # Ensure that 'start_time' and 'end_time' are datetime objects for accurate calculation
                if isinstance(surgery['start_time'], datetime) and isinstance(surgery['end_time'], datetime):
                    duration_hours = (surgery['end_time'] - surgery['start_time']).total_seconds() / 3600
                    if room_id in total_used_hours_per_room:
                        total_used_hours_per_room[room_id] += duration_hours
                    else:
                        total_used_hours_per_room[room_id] = duration_hours
            else:
                print(f"Warning: Missing data in surgery {surgery}")

        return total_used_hours_per_room

    def evaluate_utilization_rate(self, utilization_rate):
        """
        Evaluates the efficiency of a utilization rate, potentially applying different metrics
        or considerations specific to the application's operational goals.
        """
        # Example: Efficiency decreases as utilization rate exceeds a threshold due to over-utilization concerns
        threshold = 0.75
        if utilization_rate <= threshold:
            return utilization_rate  # Directly use the rate as the efficiency score
        else:
            # Apply a penalty for exceeding the threshold to discourage over-utilization
            return 1 - (utilization_rate - threshold)

    def calculate_workload_balance(self):
        # Instantiate the WorkloadBalanceCalculator
        workload_calculator = WorkloadBalanceCalculator()
        
        # Perform the calculation
        workload_balance_metric = workload_calculator.calculate_workload_balance()
        
        # You might want to store this metric in the instance for later use
        return workload_balance_metric

    # Existing methods...
    def calculate_resource_utilization_efficiency(self):
        if not self.start_date or not self.end_date:
            raise ValueError("Start date and end date must be set before performing this calculation.")

    def calculate_preference_satisfaction(self, surgeries):
        return self.preference_satisfaction_calculator.calculate_preference_satisfaction(surgeries)

# Example weights for each metric
weight_workload_balance = 2.0
weight_preference_satisfaction = 1.5
weight_resource_utilization_efficiency = 2.0
weight_equipment_utilization_efficiency = 1.0
weight_surgeon_schedule_compactness = 1.5
weight_operational_cost_minimization = 2.5
weight_room_utilization_efficiency = 2.0

def calculate_score(self):
    """Calculates the overall score of the solution based on various metrics."""
    self.score = (
        self.workload_balance * weight_workload_balance +
        self.preference_satisfaction * weight_preference_satisfaction +
        self.resource_utilization_efficiency * weight_resource_utilization_efficiency +
        self.equipment_utilization_efficiency * weight_equipment_utilization_efficiency +
        self.surgeon_schedule_compactness * weight_surgeon_schedule_compactness +
        self.operational_cost_minimization * weight_operational_cost_minimization +
        self.room_utilization_efficiency * weight_room_utilization_efficiency
    )
    return self.score

from datetime import datetime
from solution import Solution

# Initialize the Solution instance
solution_instance = Solution()

# Optionally, if your design includes setting an analysis period:
solution_instance.set_analysis_period(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31)
)

# Calculate all metrics
solution_instance.calculate_all_metrics()

# Access and print some calculated metrics for verification
print(f"Equipment Utilization Efficiency: {solution_instance.equipment_utilization_efficiency}")
print(f"Operational Cost Minimization: {solution_instance.operational_cost_minimization}")
print(f"Room Utilization Efficiency: {solution_instance.room_utilization_efficiency}")
print(f"Workload Balance: {solution_instance.workload_balance}")
