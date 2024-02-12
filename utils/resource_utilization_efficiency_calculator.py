import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient
import datetime
class ResourceUtilizationEfficiencyCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate(self, start_date, end_date):
        room_utilization = self._calculate_room_utilization(start_date, end_date)
        equipment_utilization = self._calculate_equipment_utilization(start_date, end_date)
        
        # Combine room and equipment utilization for overall resource utilization efficiency
        # Assuming room and equipment IDs are unique and won't clash
        overall_utilization = {**room_utilization, **equipment_utilization}
        return overall_utilization

    def _calculate_room_utilization(self, start_date, end_date):
        # Example aggregation pipeline to calculate room usage
        pipeline = [
            {"$match": {
                "start_time": {"$gte": start_date},
                "end_time": {"$lte": end_date},
                "status": "Completed"  # Example filter to consider only completed surgeries
            }},
            {"$group": {
                "_id": "$room_id",
                "used_hours": {"$sum": {
                    "$divide": [{"$subtract": ["$end_time", "$start_time"]}, 3600]
                }}
            }}
        ]
        room_usage = {}
        for usage in self.db.surgeries.aggregate(pipeline):
            room_id = usage["_id"]
            room_usage[room_id] = usage["used_hours"]
        return room_usage   

    def _calculate_equipment_utilization(self, start_date, end_date):
        # Similar aggregation pipeline for equipment utilization
        pipeline = [
            {"$match": {
                "start_time": {"$gte": start_date},
                "end_time": {"$lte": end_date},
                "status": "Completed"
            }},
            {"$unwind": "$equipment_used"},
            {"$group": {
                "_id": "$equipment_used.equipment_id",
                "used_hours": {"$sum": {
                    "$divide": [{"$subtract": ["$end_time", "$start_time"]}, 3600]
                }}
            }}
        ]
        equipment_usage = {}
        for usage in self.db.surgeries.aggregate(pipeline):
            equipment_id = usage["_id"]
            equipment_usage[equipment_id] = usage["used_hours"]
        return equipment_usage

# Example use case
if __name__ == "__main__":
    calculator = ResourceUtilizationEfficiencyCalculator()
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    overall_utilization = calculator.calculate(start_date, end_date)
    print("Overall Resource Utilization Efficiency:")
    for resource_id, efficiency in overall_utilization.items():
        print(f"{resource_id}: {efficiency}%")
