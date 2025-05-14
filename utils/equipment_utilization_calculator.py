from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient
class EquipmentUtilizationCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate_equipment_utilization_efficiency(self, start_date, end_date):
        equipment_availability = self._calculate_equipment_availability(start_date, end_date)
        equipment_used_hours = self._calculate_equipment_used_hours(start_date, end_date)

        equipment_utilization_efficiency = {}
        for equipment_id, available_hours in equipment_availability.items():
            used_hours = equipment_used_hours.get(equipment_id, 0)
            efficiency = (used_hours / available_hours) * 100 if available_hours > 0 else 0
            equipment_utilization_efficiency[equipment_id] = efficiency

        return equipment_utilization_efficiency

    def _calculate_equipment_availability(self, start_date, end_date):
        total_days = (end_date - start_date).days + 1
        available_hours_per_day = 8

        equipment_availability = {}
        equipment_docs = self.db.equipment.find({})
        for equipment in equipment_docs:
            equipment_id = equipment.get('equipment_id')
            equipment_availability[equipment_id] = available_hours_per_day * total_days

        return equipment_availability

    def _calculate_equipment_used_hours(self, start_date, end_date):
        pipeline = [
            {"$match": {
                "start_time": {"$gte": start_date},
                "end_time": {"$lte": end_date}
            }},
            {"$unwind": "$required_equipment_ids"},
            {"$group": {
                "_id": "$required_equipment_ids",
                "total_used_hours": {"$sum": {
                    "$divide": [{"$subtract": ["$end_time", "$start_time"]}, 3600000]  # Convert milliseconds to hours
                }}
            }}
        ]
        equipment_used_hours = {}
        for doc in self.db.surgeries.aggregate(pipeline):
            equipment_id = doc['_id']
            total_used_hours = doc['total_used_hours']
            equipment_used_hours[equipment_id] = total_used_hours

        return equipment_used_hours

# Example of how to use EquipmentUtilizationCalculator within your application
if __name__ == "__main__":
    calculator = EquipmentUtilizationCalculator()
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    efficiency = calculator.calculate_equipment_utilization_efficiency(start_date, end_date)
    print("Equipment Utilization Efficiency:")
    for equipment_id, util in efficiency.items():
        print(f"Equipment ID: {equipment_id}, Utilization Efficiency: {util:.2f}%")

