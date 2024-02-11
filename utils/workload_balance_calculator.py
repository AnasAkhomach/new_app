import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient


class WorkloadBalanceCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate_workload_balance(self):
        # Fetch all surgeries to count how many each surgeon has
        surgeries = list(self.db.surgeries.find({}))
        
        # Initialize a dictionary to count surgeries per surgeon
        surgery_count_per_surgeon = {}
        
        for surgery in surgeries:
            # Default to None or a placeholder value if 'surgeon_id' is missing
            surgeon_id = surgery.get('surgeon_id', None)
            if surgeon_id is not None:
                surgery_count_per_surgeon[surgeon_id] = surgery_count_per_surgeon.get(surgeon_id, 0) + 1

        # Ensure there are surgeons with surgeries before calculating balance metrics
        if len(surgery_count_per_surgeon) > 0:
            avg_count = sum(surgery_count_per_surgeon.values()) / len(surgery_count_per_surgeon)
            variance = sum((count - avg_count) ** 2 for count in surgery_count_per_surgeon.values()) / len(surgery_count_per_surgeon)
            std_dev = variance ** 0.5
            return std_dev
        else:
            # Return a default value or indicate an error/empty state if no surgeries are assigned to surgeons
            print("No surgeries found for any surgeon.")
            return None

if __name__ == "__main__":
    calculator = WorkloadBalanceCalculator()
    workload_balance_metric = calculator.calculate_workload_balance()
    print(f"Workload Balance Metric (Standard Deviation): {workload_balance_metric}")
