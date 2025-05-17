import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Removed MongoDBClient import
from datetime import datetime, timedelta


class RoomUtilizationCalculator:
    def __init__(self, db_session=None):
        # Accept a database session (e.g., SQLAlchemy session) for potential MySQL integration
        self.db_session = db_session

    def calculate(self, start_date, end_date, room_assignments_data=None):
        # If room_assignments_data is not provided, attempt to fetch from db_session if available
        if room_assignments_data is None:
            if self.db_session:
                # This part needs to be implemented to fetch data using SQLAlchemy
                # Example: room_assignments_data = self.db_session.query(SurgeryRoomAssignmentModel).filter(...).all()
                # Convert SQLAlchemy objects to dicts if necessary for the current logic
                print("Data fetching from db_session needs to be implemented.")
                room_assignments_data = []  # Placeholder
            else:
                print("No room assignments data provided and no db_session available.")
                return {}

        # Calculate total used hours per room
        used_hours_per_room = {}
        for (
            assignment
        ) in room_assignments_data:  # Assumes assignment is a dict or object
            room_id = assignment.get("room_id")
            start_time = assignment.get("start_time")  # Should be datetime objects
            end_time = assignment.get("end_time")  # Should be datetime objects

            if not all(
                [
                    room_id,
                    isinstance(start_time, datetime),
                    isinstance(end_time, datetime),
                ]
            ):
                print(f"Skipping invalid assignment data: {assignment}")
                continue

            duration = (
                end_time - start_time
            ).total_seconds() / 3600  # Convert to hours

            if room_id in used_hours_per_room:
                used_hours_per_room[room_id] += duration
            else:
                used_hours_per_room[room_id] = duration

        # Assume each room is available 8 hours per day for the entire date range
        # This could be made more dynamic, e.g., by fetching room availability from the database
        total_days = (end_date - start_date).days + 1
        total_available_hours_per_room = total_days * 8  # Default available hours

        # Calculate utilization efficiency for each room
        room_efficiency = {}
        for room_id, used_hours in used_hours_per_room.items():
            if total_available_hours_per_room > 0:
                efficiency = (
                    used_hours / total_available_hours_per_room
                ) * 100  # as a percentage
                room_efficiency[room_id] = efficiency
            else:
                room_efficiency[room_id] = 0  # Avoid division by zero

        return room_efficiency


if __name__ == "__main__":
    # Example usage:
    # calculator = RoomUtilizationCalculator(db_session=your_sqla_session) # If using SQLAlchemy
    calculator = RoomUtilizationCalculator()

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)

    # Example mock data for room_assignments_data
    # In a real scenario, this data would be fetched from the database or passed from another source
    mock_room_assignments = [
        {
            "room_id": "OR1",
            "start_time": datetime(2023, 1, 1, 9, 0),
            "end_time": datetime(2023, 1, 1, 11, 0),
        },
        {
            "room_id": "OR1",
            "start_time": datetime(2023, 1, 2, 14, 0),
            "end_time": datetime(2023, 1, 2, 17, 0),
        },
        {
            "room_id": "OR2",
            "start_time": datetime(2023, 1, 1, 10, 0),
            "end_time": datetime(2023, 1, 1, 12, 0),
        },
    ]

    # The method name in the original example was `calculate_room_utilization_efficiency`
    # but the class method is named `calculate`. Assuming `calculate` is the correct one.
    efficiency_metrics = calculator.calculate(
        start_date, end_date, room_assignments_data=mock_room_assignments
    )

    if efficiency_metrics:
        print("Room Utilization Efficiency:")
        for room_id, efficiency_value in efficiency_metrics.items():
            print(
                f"Room ID: {room_id}, Utilization Efficiency: {efficiency_value:.2f}%"
            )
    else:
        print("Could not calculate room utilization efficiency.")
