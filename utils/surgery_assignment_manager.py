import sys
import os

# Adjust the path to ensure the mongodb_transaction_manager is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mongodb_transaction_manager import MongoDBClient

class SurgeryAssignmentManager:
    def __init__(self):
        # Initialize MongoDB client
        self.db = MongoDBClient.get_db()

    def fetch_unassigned_surgeries(self):
        """
        Fetches surgeries from the database that haven't been assigned a schedule.
        Assumes surgeries have a 'status' field indicating their scheduling status.
        """
        unscheduled_surgeries = self.db.surgeries.find({"status": "Unscheduled"})
        return list(unscheduled_surgeries)

    def assign_resources_to_surgery(self, surgery_id, room_id, surgeon_id, equipment_ids, start_time, end_time):
        """
        Assigns a room, surgeon, and equipment to a surgery and updates its status.
        """
        update_result = self.db.surgeries.update_one(
            {"_id": surgery_id},
            {"$set": {
                "room_id": room_id,
                "surgeon_id": surgeon_id,
                "equipment_ids": equipment_ids,
                "start_time": start_time,
                "end_time": end_time,
                "status": "Scheduled"
            }}
        )
        return update_result.modified_count > 0

    def check_surgery_constraints(self, surgery_id):
        """
        Checks if a surgery's assigned resources meet all required constraints.
        Placeholder for constraint checking logic; implement based on your specific rules.
        """
        # Implement checks for room size, surgeon availability, equipment availability, etc.
        return True  # Return False if any constraints are violated

    def match_surgeries_with_surgeons(self):
        unscheduled_surgeries = self.fetch_unassigned_surgeries()
        for surgery in unscheduled_surgeries:
            # Fetch potential surgeons based on surgery specialty
            potential_surgeons = self.db.surgeons.find({"specialty": surgery["specialty"]})
            suitable_surgeon = None
            
            for surgeon in potential_surgeons:
                # Check each surgeon's availability
                if self.is_surgeon_available(surgeon["_id"], surgery["proposed_start_time"], surgery["proposed_end_time"]):
                    suitable_surgeon = surgeon
                    break  # Stop searching once a suitable surgeon is found
            
            if suitable_surgeon:
                # Assign the found surgeon to the surgery
                self.assign_surgeon_to_surgery(surgery["_id"], suitable_surgeon["_id"])
                print(f"Assigned Surgeon {suitable_surgeon['name']} to Surgery {surgery['_id']}")
            else:
                print(f"No suitable surgeon found for Surgery {surgery['_id']}")

    def is_surgeon_available(self, surgeon_id, proposed_start_time, proposed_end_time):
        # Convert proposed times to the appropriate format if necessary
        proposed_start = proposed_start_time.isoformat() if not isinstance(proposed_start_time, str) else proposed_start_time
        proposed_end = proposed_end_time.isoformat() if not isinstance(proposed_end_time, str) else proposed_end_time

        # Check for any existing appointments that overlap with the proposed times
        overlapping_appointments = self.db.appointments.find({
            "surgeon_id": surgeon_id,
            "$or": [
                {"start_time": {"$lt": proposed_end, "$gte": proposed_start}},
                {"end_time": {"$gt": proposed_start, "$lt": proposed_end}}
            ]
        }).count()

        # Surgeon is available if no overlapping appointments found
        return overlapping_appointments == 0

    def assign_surgeon_to_surgery(self, surgery_id, surgeon_id):
        """
        Updates the specified surgery with the assigned surgeon's ID.
        Args:
        - surgery_id: The unique identifier for the surgery.
        - surgeon_id: The unique identifier for the surgeon being assigned.
        """
        # Attempt to update the surgery record in the database
        result = self.db.surgeries.update_one(
            {"_id": surgery_id},  # Match the surgery by its ID
            {"$set": {
                "surgeon_id": surgeon_id,  # Assign the surgeon's ID
                "status": "Scheduled"  # Optionally update the surgery status
            }}
        )
        
        # Check if the database update was successful
        if result.modified_count == 1:
            print(f"Surgery {surgery_id} has been successfully assigned to Surgeon {surgeon_id}.")
            return True
        else:
            print(f"Failed to assign Surgery {surgery_id} to Surgeon {surgeon_id}.")
            return False




# Example usage
from mongodb_transaction_manager import MongoDBClient

if __name__ == "__main__":
    manager = SurgeryAssignmentManager()  # Assumes MongoDBClient initialization inside
    unscheduled_surgeries = manager.fetch_unassigned_surgeries()
    for surgery in unscheduled_surgeries:
        # Attempt to find a suitable surgeon based on specialty and availability
        suitable_surgeon = manager.find_suitable_surgeon_for_surgery(surgery)
        if suitable_surgeon:
            # Example process to assign resources, now including a dynamically found surgeon
            success = manager.assign_resources_to_surgery(
                surgery['_id'], "room101", suitable_surgeon, ["equipmentA", "equipmentB"], "2023-01-01T09:00", "2023-01-01T11:00"
            )
            if success:
                print(f"Surgery {surgery['_id']} scheduled successfully with Surgeon {suitable_surgeon}.")
            else:
                print(f"Failed to schedule Surgery {surgery['_id']}.")
        else:
            print(f"No suitable surgeon found for Surgery {surgery['_id']}.")
