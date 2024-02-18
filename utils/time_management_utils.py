from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient


class TimeManagementUtils:

    def __init__(self):
        # Access the database using the MongoDBClient
        self.db = MongoDBClient.get_db()

    @staticmethod
    def shift_surgery_time(current_time_str, delta_minutes):
        try:
            current_time = datetime.strptime(current_time_str, '%Y-%m-%dT%H:%M:%S')
            new_time = current_time + timedelta(minutes=delta_minutes)
            return new_time.strftime('%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            # Handle or log the error appropriately
            print(f"Error shifting surgery time: {e}")
            return None

    def find_next_available_time_slots(self, room_id, duration, buffer_time=30):
        available_slots = []
        setup_time = 15
        cleanup_time = 15
        total_required_time = duration + setup_time + cleanup_time + buffer_time

        latest_appointment = self.db.surgery_room_assignments.find_one(
            {"room_id": room_id},
            sort=[("end_time", -1)]
        )

        if latest_appointment:
            latest_end_time = datetime.strptime(latest_appointment['end_time'], "%Y-%m-%dT%H:%M:%S")
            next_available_start = latest_end_time + timedelta(minutes=cleanup_time + buffer_time)
        else:
            next_available_start = datetime.now() + timedelta(minutes=setup_time)

        for _ in range(5):  # Example for generating multiple slots
            next_available_end = next_available_start + timedelta(minutes=duration)
            available_slots.append({
                'start': next_available_start.isoformat(),
                'end': next_available_end.isoformat()
            })
            next_available_start = next_available_end + timedelta(minutes=total_required_time)

        return available_slots


    def is_time_slot_tabu(self, start_time_str, end_time_str, additional_criteria={}):
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%S')
        query = {
            "$or": [
                {"start_time": {"$lt": end_time}, "end_time": {"$gt": start_time}}  # Overlaps
            ]
        }
        # Incorporate additional criteria (e.g., surgeon_id, room_id)
        query.update(additional_criteria)

        tabu_status = self.db.tabu_entries.find_one(query)
        return bool(tabu_status)



    def is_resource_tabu(self, resource_identifiers, start_time_str, end_time_str):
        # Leverages is_time_slot_tabu for checking both time and resource constraints
        return self.is_time_slot_tabu(start_time_str, end_time_str, resource_identifiers)

