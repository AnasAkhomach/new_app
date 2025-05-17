import sys
import os
import datetime  # Added for type hinting and example data

# Add the parent directory to sys.path if needed for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Removed MongoDBClient import


class OperationalCostCalculator:
    def __init__(self, db_session=None):
        # Accept a database session (e.g., SQLAlchemy session) for potential MySQL integration
        self.db_session = db_session

    def calculate_average_duration(self, surgeries_data):
        # surgeries_data: list of dicts/objects representing surgeries, expected to have 'start_time' and 'end_time'
        if not surgeries_data:
            print("No surgeries provided for calculation.")
            return 0  # Return 0 for average duration if no surgeries

        total_duration_hours = 0
        valid_surgeries_count = 0

        for surgery in surgeries_data:
            start_time = surgery.get("start_time")
            end_time = surgery.get("end_time")

            if (
                isinstance(start_time, datetime.datetime)
                and isinstance(end_time, datetime.datetime)
                and end_time > start_time
            ):
                duration = (
                    end_time - start_time
                ).total_seconds() / 3600  # Convert seconds to hours
                total_duration_hours += duration
                valid_surgeries_count += 1
            else:
                print(
                    f"Skipping surgery due to invalid or missing start/end times: {surgery.get('surgery_id', 'N/A')}"
                )

        average_duration_hours = (
            total_duration_hours / valid_surgeries_count
            if valid_surgeries_count > 0
            else 0
        )

        # The original intent seemed to be cost, but the implementation was average duration.
        # This method now clearly calculates average duration.
        # If cost calculation is needed, a separate method or logic would be required.
        return average_duration_hours


# Example usage
if __name__ == "__main__":
    # calculator = OperationalCostCalculator(db_session=your_sqla_session) # If using DB
    calculator = OperationalCostCalculator()

    mock_surgeries = [
        {
            "surgery_id": "s1",
            "start_time": datetime.datetime(2023, 1, 1, 9, 0),
            "end_time": datetime.datetime(2023, 1, 1, 11, 0),  # 2 hours
        },
        {
            "surgery_id": "s2",
            "start_time": datetime.datetime(2023, 1, 1, 14, 0),
            "end_time": datetime.datetime(2023, 1, 1, 17, 0),  # 3 hours
        },
        {
            "surgery_id": "s3",  # Missing end_time
            "start_time": datetime.datetime(2023, 1, 2, 10, 0),
        },
    ]

    # If db_session is provided and surgeries_data is None, you might fetch from DB:
    # if calculator.db_session and not mock_surgeries:
    #     print("Fetching surgeries from database (placeholder logic)...")
    #     # mock_surgeries = fetch_surgeries_from_sqla(calculator.db_session)

    avg_duration = calculator.calculate_average_duration(mock_surgeries)

    print(f"Average Surgery Duration: {avg_duration:.2f} hours")

    # Example with no surgeries
    avg_duration_empty = calculator.calculate_average_duration([])
    print(f"Average Surgery Duration (empty list): {avg_duration_empty:.2f} hours")
