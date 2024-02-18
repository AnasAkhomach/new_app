from solution import Solution  # Assuming your solution class is in solution.py
import copy
from copy import deepcopy

from utils.time_management_utils import TimeManagementUtils
from utils.room_assignment_manager import RoomAssignmentManager
from utils.staff_assignment_manager import StaffAssignmentManager
from utils.equipment_assignment_manager import EquipmentAssignmentManager

class NeighborGenerator:
    def __init__(self, db, schedule_validator, room_assignment_manager, staff_assignment_manager, equipment_assignment_manager):
        self.db = db
        self.schedule_validator = schedule_validator
        self.room_assignment_manager = room_assignment_manager
        self.staff_assignment_manager = staff_assignment_manager
        self.equipment_assignment_manager = equipment_assignment_manager

    def generate_neighbors(self, current_solution: Solution):
        """Generates neighbor solutions from the current solution."""
        neighbors = []
        
        neighbors.extend(self._shift_surgeries_in_time(copy.deepcopy(current_solution)))
        neighbors.extend(self._reassign_surgeries_to_different_rooms(copy.deepcopy(current_solution)))
        neighbors.extend(self._swap_surgeons_between_surgeries(copy.deepcopy(current_solution)))
        neighbors.extend(self._reallocate_equipment_to_surgeries(copy.deepcopy(current_solution)))
        
        # Filter out invalid neighbors based on defined constraints
        valid_neighbors = [n for n in neighbors if self.schedule_validator.is_valid_schedule(n)]
        
        return valid_neighbors

    def _shift_surgeries_in_time(self, solution):
        shifted_solutions = []
        for surgery in solution.surgeries:
            # Example of using the shifted time to create a new solution variant
            new_time_str = TimeManagementUtils.shift_surgery_time(surgery.start_time_str, 30)  # Example shift
            # Clone the solution and apply the new time, then add to shifted_solutions
        return shifted_solutions

    def _reassign_surgeries_to_different_rooms(self, solution):
        """Generates neighbor solutions by reassigning surgeries to different rooms."""
        neighbor_solutions = []
        
        # Iterate through each surgery in the solution
        for surgery in solution.surgeries:
            # Get a list of all available rooms
            available_rooms = self._get_available_rooms_for_surgery(surgery)
            
            # Attempt to reassign the surgery to each available room
            for room_id in available_rooms:
                if room_id != surgery.room_id:  # Ensure it's a different room
                    # Create a new solution variant with the surgery reassigned to the new room
                    new_solution = deepcopy(solution)
                    # Find the specific surgery in new_solution and update its room_id
                    for ns_surgery in new_solution.surgeries:
                        if ns_surgery.id == surgery.id:
                            ns_surgery.room_id = room_id
                            break
                    
                    # Validate the new_solution if necessary
                    if self._validate_new_solution(new_solution):
                        neighbor_solutions.append(new_solution)

        return neighbor_solutions

    def _get_available_rooms_for_surgery(self, surgery):
        """Fetches available rooms that meet the surgery's requirements."""
        available_rooms = []
        all_rooms = self.db.rooms.find()  # Assuming this returns a cursor to iterate over all rooms

        for room in all_rooms:
            # Check if the room meets the surgery's size and equipment requirements
            if self.room_assignment_manager.check_room_suitability(room['room_id'], surgery):
                # Assuming check_room_suitability returns a boolean indicating suitability
                available_rooms.append(room['room_id'])

        return available_rooms


    def _validate_new_solution(self, new_solution):
        """Validates the new solution against all scheduling constraints."""
        # Example validation checks
        for surgery in new_solution.surgeries:
            # Check surgeon availability
            if not self.staff_assignment_manager.is_surgeon_available(surgery.surgeon_id, surgery.start_time, surgery.end_time):
                return False

            # Check room availability
            if not self.room_assignment_manager.is_room_available(surgery.room_id, surgery.start_time, surgery.end_time):
                return False

            # Check equipment availability
            for equipment_id in surgery.equipment_needed:
                if not self.equipment_assignment_manager.is_equipment_available(equipment_id, surgery.start_time, surgery.end_time):
                    return False

        return True  # The solution passes all checks


    def _swap_surgeons_between_surgeries(self, solution):
        """Generates neighbor solutions by swapping surgeons between two surgeries."""
        neighbor_solutions = []
        
        # Iterate through all pairs of surgeries in the solution
        for i in range(len(solution.surgeries)):
            for j in range(i + 1, len(solution.surgeries)):
                surgery1 = solution.surgeries[i]
                surgery2 = solution.surgeries[j]
                
                # Check if swapping surgeons is feasible
                if self._can_swap_surgeons(surgery1, surgery2):
                    # Perform the swap
                    new_solution = deepcopy(solution)
                    new_solution.surgeries[i].surgeon_id, new_solution.surgeries[j].surgeon_id = \
                        new_solution.surgeries[j].surgeon_id, new_solution.surgeries[i].surgeon_id
                    
                    # Validate the new solution, e.g., check for conflicts or unavailability
                    if self._validate_new_solution(new_solution):
                        neighbor_solutions.append(new_solution)
        
        return neighbor_solutions
    
    def _can_swap_surgeons(self, surgery1, surgery2):
        """Checks if surgeons can be swapped between two surgeries without causing scheduling conflicts."""
        # Check availability of surgery1's surgeon for surgery2's time slot and vice versa
        surgeon1_available_for_surgery2 = self.staff_assignment_manager.is_surgeon_available(
            surgery1.surgeon_id, surgery2.start_time, surgery2.end_time)
        surgeon2_available_for_surgery1 = self.staff_assignment_manager.is_surgeon_available(
            surgery2.surgeon_id, surgery1.start_time, surgery1.end_time)
        
        return surgeon1_available_for_surgery2 and surgeon2_available_for_surgery1

    def _validate_new_solution(self, new_solution):
        """
        Validates if the new solution meets all scheduling constraints,
        such as surgeon availability, room availability, equipment availability, and more.
        """
        # Validate surgeon availability for each surgery
        for surgery in new_solution.surgeries:
            if not self.staff_assignment_manager.is_surgeon_available(surgery.surgeon_id, surgery.start_time, surgery.end_time):
                return False

        # Validate room availability for each surgery
        for surgery in new_solution.surgeries:
            if not self.room_assignment_manager.is_room_available(surgery.room_id, surgery.start_time, surgery.end_time):
                return False

        # Validate equipment availability for each surgery
        for surgery in new_solution.surgeries:
            for equipment_id in surgery.equipment_needed:
                if not self.equipment_assignment_manager.is_equipment_available(equipment_id, surgery.start_time, surgery.end_time):
                    return False

        # Add any additional validation checks here
        # This could include checking for overutilization of resources, compliance with legal or policy constraints, etc.

        return True  # If all checks pass, the solution is valid


    def _reallocate_equipment_to_surgeries(self, solution):
        """Generates neighbor solutions by reallocating equipment among surgeries."""
        neighbor_solutions = []
        # Assuming you have a method to fetch all equipment and their availability
        equipment_list = self.equipment_assignment_manager.list_all_equipment()

        for surgery in solution.surgeries:
            for equipment in equipment_list:
                # Check if the equipment can be reallocated to the surgery
                if self.equipment_assignment_manager.is_equipment_compatible(surgery, equipment) and \
                self.equipment_assignment_manager.is_equipment_available(equipment['id'], surgery['start_time'], surgery['end_time']):
                    # Create a new solution with the equipment reallocated
                    new_solution = deepcopy(solution)
                    # Find the surgery in new_solution and update its equipment list
                    for ns_surgery in new_solution.surgeries:
                        if ns_surgery['id'] == surgery['id']:
                            ns_surgery['equipment_needed'].append(equipment['id'])
                            break

                    # Ensure the new solution does not exceed equipment availability
                    if self._validate_equipment_availability(new_solution):
                        neighbor_solutions.append(new_solution)

        return neighbor_solutions

    def _validate_equipment_availability(self, solution):
        """Validates if the solution's equipment allocations do not exceed available quantities."""
        equipment_usage = {}
        for surgery in solution.surgeries:
            for equipment_id in surgery['equipment_needed']:
                equipment_usage[equipment_id] = equipment_usage.get(equipment_id, 0) + 1

        for equipment_id, usage_count in equipment_usage.items():
            if not self.equipment_assignment_manager.check_equipment_stock(equipment_id, usage_count):
                return False

        return True

