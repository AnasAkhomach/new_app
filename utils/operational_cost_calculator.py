import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient
from datetime import datetime


class OperationalCostCalculator:
    def __init__(self, db):
        self.db = db

    def calculate_operational_cost_minimization(self):
        # Get all surgeries that have both a start_time and an end_time
        surgeries = self.db.surgeries.find({
            'start_time': {'$exists': True},
            'end_time': {'$exists': True}
        })

        total_duration = 0
        surgery_count = 0

        # Iterate over each surgery to calculate its duration and add it to the total
        for surgery in surgeries:
            # Make sure start_time and end_time are datetime objects
            if isinstance(surgery['start_time'], datetime) and isinstance(surgery['end_time'], datetime):
                duration_hours = (surgery['end_time'] - surgery['start_time']).total_seconds() / 3600
                total_duration += duration_hours
                surgery_count += 1

        # Calculate average surgery duration
        average_duration = total_duration / surgery_count if surgery_count else float('inf')

        return average_duration
    

# If this script is run as the main script, perform the cost calculation
if __name__ == "__main__":
    db = MongoDBClient.get_db()
    calculator = OperationalCostCalculator(db)
    avg_duration = calculator.calculate_operational_cost_minimization()
    print(f"Average Surgery Duration: {avg_duration:.2f} hours (Operational Cost Proxy)")