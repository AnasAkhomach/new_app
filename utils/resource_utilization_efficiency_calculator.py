import sys
import os
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Removed MongoDBClient import


class ResourceUtilizationEfficiencyCalculator:
    def __init__(self, db_session=None):
        # Accept a database session (e.g., SQLAlchemy session) for potential MySQL integration
        self.db_session = db_session

    def calculate(self, start_date, end_date, surgeries_data=None):
        # surgeries_data: list of dicts/objects representing surgeries, expected to have room_id, equipment_used, start_time, end_time
        if surgeries_data is None:
            if self.db_session:
                # Placeholder: Fetch surgery data using SQLAlchemy
                # surgeries_data = self.db_session.query(SurgeryModel).filter(...).all()
                # Convert to list of dicts if necessary
                print(
                    "Surgery data fetching from db_session needs to be implemented for resource utilization."
                )
                surgeries_data = []
            else:
                print(
                    "No surgery data provided and no db_session available for resource utilization."
                )
                return {}

        room_utilization = self._calculate_room_utilization(
            start_date, end_date, surgeries_data
        )
        equipment_utilization = self._calculate_equipment_utilization(
            start_date, end_date, surgeries_data
        )

        # Combine room and equipment utilization for overall resource utilization efficiency
        # Assuming room and equipment IDs are unique and won't clash. If they can, prefix them.
        overall_utilization = {**room_utilization, **equipment_utilization}
        return overall_utilization

    def _calculate_room_utilization(self, start_date, end_date, surgeries_data):
        room_usage_hours = {}
        for surgery in surgeries_data:
            # Validate data: ensure start_time, end_time are datetime and status is 'Completed' (or relevant status)
            s_start = surgery.get("start_time")
            s_end = surgery.get("end_time")
            status = surgery.get("status")
            room_id = surgery.get("room_id")

            if not (
                isinstance(s_start, datetime.datetime)
                and isinstance(s_end, datetime.datetime)
                and s_start >= start_date
                and s_end <= end_date
                and status == "Completed"
                and room_id
            ):
                continue

            duration_hours = (s_end - s_start).total_seconds() / 3600
            room_usage_hours[room_id] = (
                room_usage_hours.get(room_id, 0) + duration_hours
            )

        # Here, 'efficiency' might mean total used hours, or percentage against available hours.
        # The original code returned hours, so we'll stick to that for now.
        # To calculate percentage, you'd need total available hours for each room.
        return room_usage_hours

    def _calculate_equipment_utilization(self, start_date, end_date, surgeries_data):
        equipment_usage_hours = {}
        for surgery in surgeries_data:
            s_start = surgery.get("start_time")
            s_end = surgery.get("end_time")
            status = surgery.get("status")
            equipment_list = surgery.get(
                "equipment_used", []
            )  # Expected to be a list of equipment IDs or dicts

            if not (
                isinstance(s_start, datetime.datetime)
                and isinstance(s_end, datetime.datetime)
                and s_start >= start_date
                and s_end <= end_date
                and status == "Completed"
            ):
                continue

            duration_hours = (s_end - s_start).total_seconds() / 3600
            for item in equipment_list:
                # Assuming item is an equipment_id string or a dict with 'equipment_id'
                equipment_id = (
                    item if isinstance(item, str) else item.get("equipment_id")
                )
                if equipment_id:
                    equipment_usage_hours[equipment_id] = (
                        equipment_usage_hours.get(equipment_id, 0) + duration_hours
                    )
        return equipment_usage_hours


# Example use case
if __name__ == "__main__":
    # calculator = ResourceUtilizationEfficiencyCalculator(db_session=your_sqla_session)
    calculator = ResourceUtilizationEfficiencyCalculator()

    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 1, 31)

    # Mock surgery data
    mock_surgeries = [
        {
            "surgery_id": "s1",
            "room_id": "OR1",
            "equipment_used": ["EQ1"],
            "start_time": datetime.datetime(2023, 1, 1, 9, 0),
            "end_time": datetime.datetime(2023, 1, 1, 11, 0),
            "status": "Completed",
        },
        {
            "surgery_id": "s2",
            "room_id": "OR1",
            "equipment_used": ["EQ1", "EQ2"],
            "start_time": datetime.datetime(2023, 1, 2, 14, 0),
            "end_time": datetime.datetime(2023, 1, 2, 17, 0),
            "status": "Completed",
        },
        {
            "surgery_id": "s3",
            "room_id": "OR2",
            "equipment_used": ["EQ2"],
            "start_time": datetime.datetime(2023, 1, 3, 10, 0),
            "end_time": datetime.datetime(2023, 1, 3, 12, 0),
            "status": "Scheduled",
        },  # This one won't be counted
    ]

    overall_utilization_hours = calculator.calculate(
        start_date, end_date, surgeries_data=mock_surgeries
    )

    if overall_utilization_hours:
        print("Overall Resource Utilization (Used Hours):")
        for resource_id, hours in overall_utilization_hours.items():
            # The original output had '%', but the calculation was for hours. Clarifying output.
            print(f"{resource_id}: {hours:.2f} hours")
    else:
        print("Could not calculate resource utilization.")
