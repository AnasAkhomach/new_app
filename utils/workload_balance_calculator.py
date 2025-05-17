import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Removed MongoDBClient import


class WorkloadBalanceCalculator:
    def __init__(self, db_session=None):
        # Accept a database session (e.g., SQLAlchemy session) for potential MySQL integration
        self.db_session = db_session
        # If direct db access was used here, it needs to be refactored or data passed in.

    def calculate_workload_balance(self, surgeries):
        # Initialize a dictionary to count surgeries per surgeon
        surgery_count_per_surgeon = {}

        for surgery in surgeries:
            surgeon_id = surgery.get(
                "surgeon_id"
            )  # Assumes surgery is a dict or object with 'surgeon_id'
            if surgeon_id:
                surgery_count_per_surgeon[surgeon_id] = (
                    surgery_count_per_surgeon.get(surgeon_id, 0) + 1
                )

        # Calculate the balance metric, such as standard deviation of surgery counts
        if len(surgery_count_per_surgeon) > 0:
            avg_count = sum(surgery_count_per_surgeon.values()) / len(
                surgery_count_per_surgeon
            )
            variance = sum(
                (count - avg_count) ** 2 for count in surgery_count_per_surgeon.values()
            ) / len(surgery_count_per_surgeon)
            std_dev = variance**0.5
            return std_dev
        else:
            return 0  # Return 0 for empty input for test consistency


if __name__ == "__main__":
    # Example usage:
    # When instantiating, pass a db_session if needed for data retrieval, or ensure data is passed directly.
    # For SQLAlchemy, you might pass a session from your db_config or similar.
    # from db_config import SessionLocal # Assuming SessionLocal is your SQLAlchemy session factory
    # db_session = SessionLocal()
    # calculator = WorkloadBalanceCalculator(db_session=db_session)
    calculator = (
        WorkloadBalanceCalculator()
    )  # Example without db_session, assumes data is passed directly

    # Example: Fetch surgeries from a SQLAlchemy session or use mock data
    # This part needs to be adapted based on how data is actually stored and retrieved with SQLAlchemy
    surgeries_data = []  # Placeholder - replace with actual data loading mechanism
    # if calculator.db_session:
    #     # Replace YourSurgeryModel with the actual SQLAlchemy model for surgeries
    #     # surgeries_data = calculator.db_session.query(YourSurgeryModel).all()
    #     # Convert SQLAlchemy objects to dicts if necessary for the current method signature
    #     # surgeries_data = [s.__dict__ for s in surgeries_data] # Basic conversion, adjust as needed
    #     pass
    # else:
    #     # Example mock data if not using a database session for this script execution
    #     surgeries_data = [
    #         {'surgeon_id': 'surgeon1', 'duration_hours': 2},
    #         {'surgeon_id': 'surgeon2', 'duration_hours': 3},
    #         {'surgeon_id': 'surgeon1', 'duration_hours': 4},
    #     ]

    if surgeries_data:
        workload_balance_metric = calculator.calculate_workload_balance(surgeries_data)
        if workload_balance_metric is not None:
            print(
                f"Workload Balance Metric (Std Dev of Surgeries per Surgeon): {workload_balance_metric:.2f}"
            )
        else:
            print("Could not calculate workload balance metric.")
    else:
        print("No surgery data provided to calculate workload balance.")

    # if calculator.db_session:
    #     calculator.db_session.close()
