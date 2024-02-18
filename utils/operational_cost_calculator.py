from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to find MongoDBClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient

class OperationalCostCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate(self, surgeries):
        total_duration = 0
        surgery_count = 0

        for surgery in surgeries:
            # Convert 'start_time' and 'end_time' from string to datetime objects
            start_time = datetime.strptime(surgery['start_time'], "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.strptime(surgery['end_time'], "%Y-%m-%dT%H:%M:%S")

            # Calculate duration in hours
            duration = (end_time - start_time).total_seconds() / 3600
            total_duration += duration
            surgery_count += 1

        # Calculate and return the average surgery duration
        if surgery_count > 0:
            average_duration = total_duration / surgery_count
        else:
            # Handle case with no surgeries to avoid division by zero
            average_duration = 0

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
