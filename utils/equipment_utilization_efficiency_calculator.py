import sys
import os

# Ensure the MongoDBClient can be found by adjusting the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient

class EquipmentUtilizationEfficiencyCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate(self, start_date, end_date):
        # Initialize a dictionary to hold the total available hours for each equipment
        equipment_availability = {}
        # Assume 8 hours per day of availability for simplicity
        available_hours_per_day = 8

        # Calculate total available hours for each equipment over the given period
        equipments = list(self.db.equipment.find({}))
        for equipment in equipments:
            equipment_id = equipment['_id']
            # Calculate the number of days in the period
            total_days = (end_date - start_date).days + 1
            equipment_availability[equipment_id] = total_days * available_hours_per_day

        # Initialize a dictionary to hold the total used hours for each equipment
        equipment_used_hours = {}
        surgeries = list(self.db.surgeries.find({
            "date": {"$gte": start_date, "$lte": end_date},
            "equipment_used": {"$exists": True}
        }))

        for surgery in surgeries:
            for equipment_id in surgery['equipment_used']:
                if equipment_id not in equipment_used_hours:
                    equipment_used_hours[equipment_id] = 0
                # Assuming each surgery uses each piece of equipment for its entire duration
                duration_hours = (surgery['end_time'] - surgery['start_time']).total_seconds() / 3600
                equipment_used_hours[equipment_id] += duration_hours

        # Calculate the utilization efficiency for each equipment
        equipment_utilization_efficiency = {}
        for equipment_id, available_hours in equipment_availability.items():
            used_hours = equipment_used_hours.get(equipment_id, 0)
            utilization_percentage = (used_hours / available_hours) * 100 if available_hours > 0 else 0
            equipment_utilization_efficiency[equipment_id] = utilization_percentage

        return equipment_utilization_efficiency

# Example usage
if __name__ == "__main__":
    from datetime import datetime

    calculator = EquipmentUtilizationEfficiencyCalculator()
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    efficiency = calculator.calculate(start_date, end_date)
    print("Equipment Utilization Efficiency:")
    for equipment_id, util in efficiency.items():
        print(f"Equipment ID: {equipment_id}, Utilization Efficiency: {util:.2f}%")
