class SurgeonManager:
    def __init__(self, db):
        self.db = db

    def get_surgeon_details(self, surgeon_id):
        # Retrieve details for a specific surgeon
        surgeon_details = self.db.surgeons.find_one({"surgeon_id": surgeon_id})
        return surgeon_details

    def update_surgeon_availability(self, surgeon_id, new_availability):
        # Update the availability schedule for a surgeon
        result = self.db.surgeons.update_one(
            {"surgeon_id": surgeon_id},
            {"$set": {"availability": new_availability}}
        )
        return result.modified_count > 0

    def list_surgeon_appointments(self, surgeon_id):
        # List all appointments (e.g., surgeries) assigned to a surgeon
        appointments = list(self.db.appointments.find({"surgeon_id": surgeon_id}))
        return appointments

    def add_surgeon_preference(self, surgeon_id, preference):
        # Add or update a preference for a surgeon
        result = self.db.surgeons.update_one(
            {"surgeon_id": surgeon_id},
            {"$addToSet": {"preferences": preference}}
        )
        return result.modified_count > 0

    def is_surgeon_available(self, surgeon_id, start_time, end_time):
        # Check if the surgeon is available within the specified time slot
        # This could involve checking the surgeon's availability schedule and existing appointments
        is_available = True
        # Implementation details here
        return is_available
