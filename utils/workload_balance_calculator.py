import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient

class WorkloadBalanceCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate_workload_balance(self, surgeries):
        # Initialize a dictionary to count surgeries per surgeon
        surgery_count_per_surgeon = {}
        
        for surgery in surgeries:
            surgeon_id = surgery.get('surgeon_id')
            if surgeon_id:
                surgery_count_per_surgeon[surgeon_id] = surgery_count_per_surgeon.get(surgeon_id, 0) + 1
        
        # Calculate the balance metric, such as standard deviation of surgery counts
        if len(surgery_count_per_surgeon) > 0:
            avg_count = sum(surgery_count_per_surgeon.values()) / len(surgery_count_per_surgeon)
            variance = sum((count - avg_count) ** 2 for count in surgery_count_per_surgeon.values()) / len(surgery_count_per_surgeon)
            std_dev = variance ** 0.5
            return std_dev
        else:
            print("No surgeries found for any surgeon.")
            return None



if __name__ == "__main__":
    # Example usage
    calculator = WorkloadBalanceCalculator()
    # Fetch surgeries from the database
    surgeries = list(calculator.db.surgeries.find({}))
    # Calculate workload balance
    workload_balance_metric = calculator.calculate_workload_balance(surgeries)
    print(f"Workload Balance Metric: {workload_balance_metric}")