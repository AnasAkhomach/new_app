class EquipmentAssignmentManager:
    def __init__(self, db):
        self.db = db

    def is_equipment_available(self, equipment_id, start_time, end_time):
        """
        Checks if the specified equipment is available during the given time period.
        """
        # Check for existing surgeries that overlap with the proposed time and use the same equipment
        overlapping_surgeries = self.db.surgeries.find({
            "equipment_used": equipment_id,
            "$or": [
                {"start_time": {"$lt": end_time, "$gte": start_time}},
                {"end_time": {"$gt": start_time, "$lte": end_time}}
            ]
        }).count()
        return overlapping_surgeries == 0

    def assign_equipment_to_surgery(self, surgery_id, equipment_list):
        """
        Assigns a list of equipment to a surgery, ensuring all equipment is available.
        """
        surgery = self.db.surgeries.find_one({"_id": surgery_id})
        if not surgery:
            print("Surgery not found.")
            return False
        
        # Check if all equipment is available during the surgery's time
        for equipment_id in equipment_list:
            if not self.is_equipment_available(equipment_id, surgery['start_time'], surgery['end_time']):
                print(f"Equipment {equipment_id} is not available for the surgery time.")
                return False
        
        # Update the surgery document with the assigned equipment
        result = self.db.surgeries.update_one({"_id": surgery_id}, {"$set": {"equipment_used": equipment_list}})
        return result.modified_count > 0

    def update_equipment_availability(self, equipment_id, availability_periods):
        """
        Updates the availability periods for a piece of equipment.
        """
        result = self.db.equipment.update_one({"_id": equipment_id}, {"$set": {"availability_periods": availability_periods}})
        return result.modified_count > 0

    def list_surgeries_using_equipment(self, equipment_id):
        """
        Lists all surgeries that have been assigned a specific piece of equipment.
        """
        surgeries = list(self.db.surgeries.find({"equipment_used": equipment_id}))
        return surgeries

    def add_equipment_assignment(self, surgery_id, equipment_id, tenure):
        # Logic to assign equipment to a surgery with a specific tenure
        self.db.equipment_assignments.update_one(
            {"surgery_id": surgery_id},
            {"$set": {"equipment_id": equipment_id, "tenure": tenure}},
            upsert=True
        )

    def is_equipment_tabu(self, surgery_id, equipment_id):
        # Check if the assignment of specific equipment to a surgery is marked as tabu
        tabu_status = self.db.tabu_entries.find_one({
            "type": "equipment",
            "surgery_id": surgery_id,
            "equipment_id": equipment_id
        })
        return bool(tabu_status)