import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient
from time_management_utils import TimeManagementUtils
from scheduling_utils import pre_fetch_resource_identifiers, get_resource_identifiers



class ScheduleGenerator:
    def __init__(self):
        # Access the database using the MongoDBClient
        self.db = MongoDBClient.get_db()
        self.time_utils = TimeManagementUtils()


    def generate_initial_solution(self):
        initial_solution = []
        potential_options = self.time_utils.generate_potential_options()  # Assume this generates all possible options
        for option in potential_options:
            # Check if the option violates any tabu constraints
            if not self.time_utils.is_time_slot_tabu(option['surgery_id'], option['time_slot']['start'], option['time_slot']['end']) and \
            not self.time_utils.is_resource_tabu({'room_id': option['room_id'], 'equipment_id': option['equipment_id']}, option['time_slot']['start'], option['time_slot']['end']):
                initial_solution.append(option)
        return initial_solution


    def generate_neighbor_solutions(self, current_solution):
        neighbors = []
        potential_options = self.time_utils.generate_potential_options()
        for option in potential_options:
            # Example of modifying a part of the current solution to generate a neighbor
            for i in range(len(current_solution)):
                neighbor = current_solution[:i] + [option] + current_solution[i+1:]
                if all(not self.time_utils.is_time_slot_tabu(opt['surgery_id'], opt['time_slot']['start'], opt['time_slot']['end']) and
                    not self.time_utils.is_resource_tabu({'room_id': opt['room_id'], 'equipment_id': opt['equipment_id']}, opt['time_slot']['start'], opt['time_slot']['end']) for opt in neighbor):
                    neighbors.append(neighbor)
        return neighbors



    def is_action_tabu(self, scheduling_option):
        # Check if the scheduling option is tabu
        tabu_entry = self.db.tabu_entries.find_one({
            "surgeon_id": scheduling_option['surgeon_id'],
            "room_id": scheduling_option['room_id'],
            "equipment_id": scheduling_option['equipment_id'],
            "time_slot": {"$gte": scheduling_option['time_slot']['start'], "$lte": scheduling_option['time_slot']['end']}
        })
        return tabu_entry is not None

    def generate_potential_options(self):
        potential_options = []
        for surgeon in self.db.surgeons.find():
            for room in self.db.operating_rooms.find():
                for equipment in self.db.surgery_equipment.find():
                    next_available_time_slots = self.find_next_available_time_slots(room['_id'])
                    for time_slot in next_available_time_slots:
                        potential_options.append({
                            'surgeon_id': surgeon['_id'],
                            'room_id': room['_id'],
                            'equipment_id': equipment['_id'],
                            'time_slot': time_slot  # Assuming time_slot is a dict with 'start' and 'end'
                        })
        return potential_options


    def schedule_surgery(surgery_details):
        time_utils = TimeManagementUtils()  # Assuming TimeManagementUtils is correctly set up
        
        # Construct resource_identifiers dynamically from surgery_details
        resource_identifiers = {
            'surgeon_id': surgery_details['surgeon_id'],
            'room_id': surgery_details['room_id'],
            'equipment_id': surgery_details['equipment_id'],
        }
        
        # Perform the tabu check
        if not time_utils.is_time_slot_tabu(surgery_details['start_time'], surgery_details['end_time'], resource_identifiers):
            # The proposed time and resources are not tabu; proceed with scheduling logic
            
            # Example: Insert surgery details into your database or scheduling calendar
            # This is a placeholder for your database insertion logic
            # db.surgeries.insert_one(surgery_details)
            
            print("Surgery scheduled successfully.")
            return True
        else:
            # Handle tabu condition, such as notifying the user or attempting to reschedule
            print("Proposed surgery time or resources conflict with tabu conditions.")
            # Attempt to find alternative resources or times
            # This could involve additional logic to suggest or select alternatives
            return False

    def perform_scheduling_operations(self, surgery_ids):
        # Pre-fetch resource identifiers for all surgeries
        identifiers_map = pre_fetch_resource_identifiers(surgery_ids)

        # Example: Use identifiers_map for tabu checks or scheduling decisions
        for surgery_id in surgery_ids:
            if surgery_id in identifiers_map:
                # Now perform tabu checks or other logic using the pre-fetched identifiers
                pass
                # Example tabu check (you would implement the actual check)
                if self.is_surgery_tabu(surgery_id, identifiers_map[surgery_id]):
                    print(f"Surgery {surgery_id} has tabu constraints.")
                else:
                    print(f"Surgery {surgery_id} is clear for scheduling.")

    def is_surgery_tabu(self, surgery_id, resource_identifiers, start_time, end_time):
        # Check if the surgery time overlaps with any tabu entries for the resources
        if self.is_time_slot_tabu(start_time, end_time, resource_identifiers):
            return True

        # Additional checks can be added here, such as mandatory rest periods or maintenance windows

        return False


    def optimize_schedule(self, surgery_options):
        # Assume surgery_options is a list of dicts with surgery details
        optimized_schedule = []
        for option in surgery_options:
            resource_identifiers = self.pre_fetch_resource_identifiers([option['surgery_id']])
            if not self.is_surgery_tabu(option['surgery_id'], resource_identifiers, option['start_time'], option['end_time']):
                # Check for optimal resource allocation and minimize conflicts
                if self.can_optimize_allocation(option, optimized_schedule):
                    optimized_schedule.append(option)
                else:
                    # Handle conflict or attempt to reschedule
                    alternative_option = self.find_alternative_option(option, optimized_schedule)
                    if alternative_option:
                        optimized_schedule.append(alternative_option)
        return optimized_schedule

