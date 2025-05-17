from datetime import (
    datetime,
    timedelta,
)  # timedelta might be useful for availability calculations
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Removed MongoDBClient import


class EquipmentUtilizationCalculator:
    def __init__(self, db_session=None):
        self.db_session = db_session

    def calculate_equipment_utilization_efficiency(
        self, start_date, end_date, surgeries_data=None, equipment_data=None
    ):
        # surgeries_data: list of surgery dicts/objects
        # equipment_data: list of equipment dicts/objects (must contain 'equipment_id')

        if equipment_data is None:
            if self.db_session:
                # Placeholder: Fetch equipment data using SQLAlchemy
                # equipment_data = self.db_session.query(EquipmentModel).all()
                # Convert to list of dicts if necessary
                print(
                    "Equipment data fetching from db_session needs to be implemented."
                )
                equipment_data = []  # Fallback to empty if not implemented
            else:
                print(
                    "No equipment data provided and no db_session available for EquipmentUtilizationCalculator."
                )
                return {}

        if surgeries_data is None:
            if self.db_session:
                # Placeholder: Fetch surgery data using SQLAlchemy for the given date range
                # surgeries_data = self.db_session.query(SurgeryModel).filter(SurgeryModel.start_time >= start_date, SurgeryModel.end_time <= end_date).all()
                # Convert to list of dicts if necessary
                print(
                    "Surgery data fetching from db_session needs to be implemented for EquipmentUtilizationCalculator."
                )
                surgeries_data = []  # Fallback to empty if not implemented
            else:
                # If no surgeries, usage is 0, efficiency will be 0 for all equipment
                print(
                    "No surgery data provided and no db_session available for EquipmentUtilizationCalculator. Assuming 0 usage."
                )
                surgeries_data = []

        equipment_availability_hours = self._calculate_equipment_availability(
            start_date, end_date, equipment_data
        )
        equipment_used_hours = self._calculate_equipment_used_hours(
            start_date, end_date, surgeries_data
        )

        equipment_utilization_efficiency = {}
        for equipment_id, available_hours in equipment_availability_hours.items():
            used_hours = equipment_used_hours.get(equipment_id, 0)
            efficiency = (
                (used_hours / available_hours) * 100 if available_hours > 0 else 0
            )
            equipment_utilization_efficiency[equipment_id] = efficiency

        return equipment_utilization_efficiency

    def _calculate_equipment_availability(self, start_date, end_date, equipment_data):
        # equipment_data: list of dicts, each with 'equipment_id'
        # Ensure start_date and end_date are datetime objects
        if not (isinstance(start_date, datetime) and isinstance(end_date, datetime)):
            raise ValueError("start_date and end_date must be datetime objects")
        if end_date < start_date:
            return {}  # Or raise error, depending on desired behavior

        total_days = (end_date - start_date).days + 1  # Inclusive of start and end day
        # Define standard available hours per day, can be made more complex (e.g., per equipment type)
        standard_available_hours_per_day = 8

        equipment_availability = {}
        for equipment in equipment_data:
            equipment_id = equipment.get("equipment_id")
            if equipment_id:
                # Here, one could fetch specific availability if stored per equipment (e.g. equipment.get('available_hours_per_day', standard_available_hours_per_day))
                equipment_availability[equipment_id] = (
                    standard_available_hours_per_day * total_days
                )
        return equipment_availability

    def _calculate_equipment_used_hours(self, start_date, end_date, surgeries_data):
        # surgeries_data: list of surgery dicts, each with 'start_time', 'end_time', 'required_equipment_ids' (list of strings)
        equipment_used_hours = {}
        for surgery in surgeries_data:
            s_start = surgery.get("start_time")
            s_end = surgery.get("end_time")
            # The original code used 'required_equipment_ids', ensure this key exists in your data
            required_equipment_ids = surgery.get(
                "required_equipment_ids", surgery.get("equipment_used", [])
            )
            # Handle if equipment_used is a list of dicts like [{'equipment_id': 'EQ1'}]
            if required_equipment_ids and isinstance(required_equipment_ids[0], dict):
                actual_ids = [
                    item.get("equipment_id")
                    for item in required_equipment_ids
                    if item.get("equipment_id")
                ]
            else:  # Assumed list of strings
                actual_ids = required_equipment_ids

            if not (
                isinstance(s_start, datetime)
                and isinstance(s_end, datetime)
                and s_start >= start_date
                and s_end <= end_date
                and s_end > s_start
            ):
                continue  # Skip if surgery is outside range or times are invalid

            duration_hours = (s_end - s_start).total_seconds() / 3600.0

            for equipment_id in actual_ids:
                if equipment_id:
                    equipment_used_hours[equipment_id] = (
                        equipment_used_hours.get(equipment_id, 0) + duration_hours
                    )
        return equipment_used_hours


# Example of how to use EquipmentUtilizationCalculator
if __name__ == "__main__":
    # calculator = EquipmentUtilizationCalculator(db_session=your_sqla_session)
    calculator = EquipmentUtilizationCalculator()

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)

    mock_equipment_list = [
        {"equipment_id": "EQ101"},
        {"equipment_id": "EQ102"},
        {"equipment_id": "EQ103"},  # This one won't be used in mock surgeries
    ]

    mock_surgeries_list = [
        {
            "surgery_id": "S001",
            "start_time": datetime(2023, 1, 5, 9, 0),
            "end_time": datetime(2023, 1, 5, 11, 0),  # 2 hours
            "required_equipment_ids": ["EQ101", "EQ102"],
        },
        {
            "surgery_id": "S002",
            "start_time": datetime(2023, 1, 10, 14, 0),
            "end_time": datetime(2023, 1, 10, 17, 0),  # 3 hours
            "required_equipment_ids": ["EQ101"],
        },
        {
            "surgery_id": "S003",  # Outside date range
            "start_time": datetime(2023, 2, 1, 10, 0),
            "end_time": datetime(2023, 2, 1, 12, 0),
            "required_equipment_ids": ["EQ102"],
        },
        {
            "surgery_id": "S004",  # Uses equipment_used as list of dicts
            "start_time": datetime(2023, 1, 15, 9, 0),
            "end_time": datetime(2023, 1, 15, 10, 0),  # 1 hour
            "equipment_used": [{"equipment_id": "EQ102"}],
        },
    ]

    efficiency_results = calculator.calculate_equipment_utilization_efficiency(
        start_date,
        end_date,
        surgeries_data=mock_surgeries_list,
        equipment_data=mock_equipment_list,
    )

    if efficiency_results:
        print("Equipment Utilization Efficiency:")
        # Expected availability for Jan (31 days * 8h/day) = 248 hours
        # EQ101: Used 2h (S001) + 3h (S002) = 5h. Efficiency = (5 / 248) * 100 = 2.02%
        # EQ102: Used 2h (S001) + 1h (S004) = 3h. Efficiency = (3 / 248) * 100 = 1.21%
        # EQ103: Used 0h. Efficiency = 0%
        for equipment_id, util in efficiency_results.items():
            print(f"Equipment ID: {equipment_id}, Utilization Efficiency: {util:.2f}%")
    else:
        print("Could not calculate equipment utilization efficiency.")

    print("\nCalculating with no surgeries:")
    efficiency_no_surgeries = calculator.calculate_equipment_utilization_efficiency(
        start_date, end_date, surgeries_data=[], equipment_data=mock_equipment_list
    )
    if efficiency_no_surgeries:
        for equipment_id, util in efficiency_no_surgeries.items():
            print(f"Equipment ID: {equipment_id}, Utilization Efficiency: {util:.2f}%")
