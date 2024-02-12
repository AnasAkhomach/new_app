import sys
import os

# Add the parent directory to sys.path to find MongoDBClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient

class OperationalCostCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate(self, surgeries):
        if not surgeries:
            print("No surgeries provided for operational cost calculation.")
            return None

        # Calculate the average duration of the provided surgeries
        total_duration = 0
        for surgery in surgeries:
            if 'start_time' in surgery and 'end_time' in surgery:
                duration = (surgery['end_time'] - surgery['start_time']).total_seconds() / 3600  # Convert seconds to hours
                total_duration += duration

        average_duration = total_duration / len(surgeries) if surgeries else 0

        # Assuming the operational cost is directly related to the surgery duration
        # Here, you might convert duration to cost if you have a cost model
        return average_duration

# Example usage
if __name__ == "__main__":
    calculator = OperationalCostCalculator()
    surgeries = [
        # Your surgeries data here
    ]
    operational_cost_minimization = calculator.calculate(surgeries)

    if operational_cost_minimization is not None:
        print(f"Operational Cost Minimization (Average Surgery Duration): {operational_cost_minimization:.2f} hours")
    else:
        print("Operational Cost Minimization could not be calculated due to missing data.")
