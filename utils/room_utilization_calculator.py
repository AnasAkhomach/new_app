import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient
from datetime import datetime, timedelta


class RoomUtilizationCalculator:
    def __init__(self):
        self.db = MongoDBClient.get_db()

    def calculate(self, start_date, end_date):
        # Fetch all room assignments within the given date range
        room_assignments = self.db.surgery_room_assignments.find({
            "start_time": {"$gte": start_date},
            "end_time": {"$lte": end_date}
        })

        # Calculate total used hours per room
        used_hours_per_room = {}
        for assignment in room_assignments:
            room_id = assignment['room_id']
            start_time = assignment['start_time']
            end_time = assignment['end_time']
            duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours
            
            if room_id in used_hours_per_room:
                used_hours_per_room[room_id] += duration
            else:
                used_hours_per_room[room_id] = duration
        
        # Assume each room is available 8 hours per day for the entire date range
        total_days = (end_date - start_date).days + 1
        total_available_hours_per_room = total_days * 8

        # Calculate utilization efficiency for each room
        room_efficiency = {}
        for room_id, used_hours in used_hours_per_room.items():
            efficiency = (used_hours / total_available_hours_per_room) * 100  # as a percentage
            room_efficiency[room_id] = efficiency

        return room_efficiency


if __name__ == "__main__":
    calculator = RoomUtilizationCalculator()
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    efficiency = calculator.calculate_room_utilization_efficiency(start_date, end_date)
    print("Room Utilization Efficiency:")
    for room_id, efficiency in efficiency.items():
        print(f"Room ID: {room_id}, Utilization Efficiency: {efficiency:.2f}%")
