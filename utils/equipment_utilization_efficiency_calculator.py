import sys
import os
from datetime import datetime  # Added missing import

# Ensure the project root can be found by adjusting the path if necessary for shared modules.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Removed MongoDBClient import


class EquipmentUtilizationEfficiencyCalculator:
    def __init__(self, db_session=None):
        # Accept a database session (e.g., SQLAlchemy session) for potential MySQL integration
        self.db_session = db_session

    def calculate(
        self, start_date, end_date, equipments_data=None, surgeries_data=None
    ):
        # Initialize a dictionary to hold the total available hours for each equipment
        equipment_availability = {}
        # Assume 8 hours per day of availability for simplicity
        # This could be made more dynamic, e.g., fetched from equipment-specific settings
        available_hours_per_day = 8

        if equipments_data is None:
            if self.db_session:
                # Placeholder: Fetch equipment data using SQLAlchemy
                # equipments_data = self.db_session.query(EquipmentModel).all()
                # Convert to list of dicts if necessary
                print(
                    "Equipment data fetching from db_session needs to be implemented."
                )
                equipments_data = []
            else:
                print("No equipment data provided and no db_session available.")
                return {}

        for equipment in equipments_data:  # Assumes equipment is a dict or object
            equipment_id = equipment.get("_id") or equipment.get(
                "id"
            )  # Adapt based on your data model
            if not equipment_id:
                continue
            total_days = (end_date - start_date).days + 1
            equipment_availability[equipment_id] = total_days * available_hours_per_day

        # Initialize a dictionary to hold the total used hours for each equipment
        equipment_used_hours = {}
        if surgeries_data is None:
            if self.db_session:
                # Placeholder: Fetch surgery data using SQLAlchemy
                # surgeries_data = self.db_session.query(SurgeryModel).filter(...).all()
                # Convert to list of dicts if necessary
                print("Surgery data fetching from db_session needs to be implemented.")
                surgeries_data = []
            else:
                print(
                    "No surgery data provided and no db_session available for equipment usage."
                )
                # Proceeding with empty surgeries_data will result in 0 used hours
                surgeries_data = []

        for surgery in surgeries_data:  # Assumes surgery is a dict or object
            # Ensure 'equipment_used', 'start_time', and 'end_time' are present and valid
            equipment_ids_used = surgery.get("equipment_used", [])
            start_time = surgery.get("start_time")  # Should be datetime
            end_time = surgery.get("end_time")  # Should be datetime

            if not all(
                [
                    isinstance(equipment_ids_used, list),
                    isinstance(start_time, datetime),
                    isinstance(end_time, datetime),
                ]
            ):
                print(
                    f"Skipping surgery with invalid data for equipment usage: {surgery.get('id', 'Unknown ID')}"
                )
                continue

            for equipment_id in equipment_ids_used:
                if equipment_id not in equipment_used_hours:
                    equipment_used_hours[equipment_id] = 0
                duration_hours = (end_time - start_time).total_seconds() / 3600
                equipment_used_hours[equipment_id] += duration_hours

        # Calculate the utilization efficiency for each equipment
        equipment_utilization_efficiency = {}
        for equipment_id, available_hours in equipment_availability.items():
            used_hours = equipment_used_hours.get(equipment_id, 0)
            utilization_percentage = (
                (used_hours / available_hours) * 100 if available_hours > 0 else 0
            )
            equipment_utilization_efficiency[equipment_id] = utilization_percentage

        return equipment_utilization_efficiency


# Example usage
if __name__ == "__main__":
    # calculator = EquipmentUtilizationEfficiencyCalculator(db_session=your_sqla_session)
    calculator = EquipmentUtilizationEfficiencyCalculator()

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)

    # Mock data for demonstration
    mock_equipments = [{"_id": "EQ1"}, {"_id": "EQ2"}]
    mock_surgeries = [
        {
            "id": "S1",
            "equipment_used": ["EQ1"],
            "start_time": datetime(2023, 1, 1, 9, 0),
            "end_time": datetime(2023, 1, 1, 11, 0),
        },
        {
            "id": "S2",
            "equipment_used": ["EQ1", "EQ2"],
            "start_time": datetime(2023, 1, 2, 14, 0),
            "end_time": datetime(2023, 1, 2, 17, 0),
        },
    ]

    efficiency = calculator.calculate(
        start_date,
        end_date,
        equipments_data=mock_equipments,
        surgeries_data=mock_surgeries,
    )

    if efficiency:
        print("Equipment Utilization Efficiency:")
        for equipment_id, util in efficiency.items():
            print(f"Equipment ID: {equipment_id}, Utilization Efficiency: {util:.2f}%")
    else:
        print("Could not calculate equipment utilization efficiency.")
