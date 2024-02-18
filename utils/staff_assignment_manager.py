class StaffAssignmentManager:
    def __init__(self, db):
        self.db = db

    def is_surgeon_available(self, surgeon_id, start_time, end_time):
        """
        Checks if a surgeon is available during the specified time period.
        """
        # Check for existing appointments that overlap with the proposed time
        overlapping_appointments = self.db.surgeries.find({
            "surgeon_id": surgeon_id,
            "$or": [
                {"start_time": {"$lt": end_time, "$gte": start_time}},
                {"end_time": {"$gt": start_time, "$lte": end_time}}
            ]
        }).count()
        return overlapping_appointments == 0

    def assign_surgeon_to_surgery(self, surgery_id, surgeon_id):
        """
        Assigns a surgeon to a surgery, ensuring the surgeon's availability.
        """
        # Fetch the surgery details to get the time period
        surgery = self.db.surgeries.find_one({"_id": surgery_id})
        if not surgery:
            print("Surgery not found.")
            return False
        
        # Check if the surgeon is available during the surgery's time
        if self.is_surgeon_available(surgeon_id, surgery['start_time'], surgery['end_time']):
            # Update the surgery document with the assigned surgeon
            result = self.db.surgeries.update_one({"_id": surgery_id}, {"$set": {"surgeon_id": surgeon_id}})
            return result.modified_count > 0
        else:
            print("Surgeon is not available for the surgery time.")
            return False

    def update_surgeon_availability(self, surgeon_id, availability_periods):
        """
        Updates the availability periods for a surgeon.
        """
        result = self.db.surgeons.update_one({"_id": surgeon_id}, {"$set": {"availability": availability_periods}})
        return result.modified_count > 0

    def list_surgeon_surgeries(self, surgeon_id):
        """
        Lists all surgeries assigned to a surgeon.
        """
        surgeries = list(self.db.surgeries.find({"surgeon_id": surgeon_id}))
        return surgeries

    def add_surgeon_assignment(self, surgery_id, surgeon_id, tenure):
        # Logic to assign a surgeon to a surgery with a specific tenure
        self.db.surgeon_assignments.update_one(
            {"surgery_id": surgery_id},
            {"$set": {"surgeon_id": surgeon_id, "tenure": tenure}},
            upsert=True
        )

    def is_surgeon_tabu(self, surgery_id, surgeon_id):
        # Logic to check if a surgeon's assignment to a surgery is currently considered tabu
        tabu_status = self.db.tabu_entries.find_one({
            "type": "surgeon",
            "surgery_id": surgery_id,
            "surgeon_id": surgeon_id
        })
        return bool(tabu_status)