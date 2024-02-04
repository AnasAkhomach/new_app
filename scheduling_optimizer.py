# This script contains the optimization logic for the surgery scheduling using Tabu Search

from models import OperatingRoom, Patient, Staff, Surgeon, Surgery, SurgeryEquipment, SurgeryEquipmentUsage, SurgeryRoomAssignment, SurgeryStaffAssignment

from initialize_data import (initialize_patients, initialize_staff_members, initialize_surgeons,
                             initialize_operating_rooms, initialize_surgeries, initialize_surgery_equipments,
                             initialize_surgery_equipment_usages, initialize_surgery_room_assignments,
                             initialize_surgery_staff_assignments)

from scheduling_utils import (
    shift_time, find_surgeon, is_room_available,
    calculate_room_utilization, check_equipment_availability, is_surgeon_available,
    is_equipment_available, get_least_used_room, create_new_neighbor,
    assign_surgery_to_room, shift_surgery_time,
    can_swap_surgeons, swap_surgeons,
)

import random
import copy
from datetime import datetime, timedelta

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TabuSearchScheduler:
    def __init__(self, surgeries, operating_rooms, surgeons, surgery_equipments, surgery_equipment_usages):
        self.surgeries = surgeries
        self.operating_rooms = operating_rooms
        self.surgeons = surgeons
        self.surgery_equipments = surgery_equipments
        self.surgery_equipment_usages = surgery_equipment_usages
        self.tabu_list = []
        self.best_solution = None
        self.best_cost = float('inf')

    patients = initialize_patients()
    staff_members = initialize_staff_members()
    surgeons = initialize_surgeons()
    operating_rooms = initialize_operating_rooms()
    surgeries = initialize_surgeries()
    surgery_equipments = initialize_surgery_equipments()
    surgery_equipment_usages = initialize_surgery_equipment_usages()
    surgery_room_assignments = initialize_surgery_room_assignments()
    surgery_staff_assignments = initialize_surgery_staff_assignments()
    

    def generate_neighbors(self):
        neighbors = []    
        # Iterate through surgeries to generate neighbor solutions
        for i, current_surgery in enumerate(self.surgeries):
            # Temporarily hold the current state to revert changes if needed
            temp_surgeries = copy.deepcopy(self.surgeries)
            temp_room_assignments = copy.deepcopy(self.surgery_room_assignments)

            # 1. Attempt to swap surgeries between rooms
            for room in self.operating_rooms:
                if self.is_change_possible(current_surgery, room.room_id):
                    # Create a new neighbor with the surgery assigned to a different room
                    self.assign_surgery_to_room(current_surgery, room.room_id)
                    neighbors.append((copy.deepcopy(self.surgeries), copy.deepcopy(self.surgery_room_assignments)))
                    # Revert to the original state after adding the neighbor
                    self.surgeries = temp_surgeries
                    self.surgery_room_assignments = temp_room_assignments
            
            # 2. Attempt to shift surgery times
            for shift in [-30, 30]:  # Example: shifting times by +/- 30 minutes
                if self.shift_surgery_time(current_surgery, shift):
                    neighbors.append((copy.deepcopy(self.surgeries), copy.deepcopy(self.surgery_room_assignments)))
                    # Revert to original state after adding the neighbor
                    self.surgeries = temp_surgeries
                    self.surgery_room_assignments = temp_room_assignments
            
            # 3. Attempt to swap surgeries between surgeons with similar expertise
            for other_surgery in self.surgeries:
                if self.can_swap_surgeons(current_surgery, other_surgery):
                    self.swap_surgeons(current_surgery, other_surgery)
                    neighbors.append((copy.deepcopy(self.surgeries), copy.deepcopy(self.surgery_room_assignments)))
                    # Revert to original state after adding the neighbor
                    self.surgeries = temp_surgeries
                    self.surgery_room_assignments = temp_room_assignments

        return neighbors

    def is_valid_schedule(self, surgeries, room_assignments):
        """
        Check if the given schedule is valid by ensuring all surgeries can be assigned to their
        surgeons and rooms without conflicts.

        Args:
        surgeries (list): List of Surgery objects.
        room_assignments (list): List of SurgeryRoomAssignment objects corresponding to the surgeries.

        Returns:
        bool: True if the schedule is valid, False otherwise.
        """
        # Check for surgeon availability and surgery time conflicts
        for surgery in surgeries:
            surgeon = next((s for s in self.surgeons if s.staff_id == surgery.surgeon_id), None)
            if surgeon is None or not surgeon.is_available(surgery.scheduled_date):
                return False
            
            # Ensuring no two surgeries overlap in the surgeon's schedule
            for other_surgery in surgeries:
                if other_surgery.surgeon_id == surgery.surgeon_id and other_surgery != surgery:
                    if not (surgery.end_time <= other_surgery.start_time or surgery.start_time >= other_surgery.end_time):
                        return False

        # Check for operating room availability and avoid overlapping surgeries in the same room
        for assignment in room_assignments:
            room = next((r for r in self.operating_rooms if r.room_id == assignment.room_id), None)
            if room is None:
                return False
            
            for other_assignment in room_assignments:
                if other_assignment.room_id == assignment.room_id and other_assignment != assignment:
                    if not (assignment.end_time <= other_assignment.start_time or assignment.start_time >= other_assignment.end_time):
                        return False

        return True

    def run(self):
        # The main method to run the Tabu Search optimization ...
        # This should include the initialization of the first solution, the main optimization loop,
        # the logic to manage the tabu list, and the logic to update the best solution
        pass
    
    def find_initial_solution(self):
        self.surgeries.sort(key=lambda x: x.urgency_level, reverse=True)  # Sort surgeries by urgency
        
        new_room_assignments = []
        
        for surgery in self.surgeries:
            for room in self.operating_rooms:
                proposed_start = datetime.now()  # Example start time, adjust as necessary
                proposed_end = proposed_start + timedelta(minutes=surgery.duration)
                
                surgeon = next((s for s in self.surgeons if s.staff_id == surgery.surgeon_id), None)
                if surgeon and is_surgeon_available(surgeon, proposed_start, proposed_end):
                    if is_equipment_available(surgery, proposed_start, proposed_end, self.surgery_equipments, self.surgery_equipment_usages):
                        least_used_room_id = get_least_used_room(new_room_assignments, self.operating_rooms)
                        # Assuming room_id matches the least used room's ID
                        if is_room_available(new_room_assignments, least_used_room_id, proposed_start.strftime('%Y-%m-%d %H:%M'), proposed_end.strftime('%Y-%m-%d %H:%M')):
                            new_assignment = SurgeryRoomAssignment(
                                assignment_id=f"RA{len(new_room_assignments)+1}",
                                surgery_id=surgery.surgery_id,
                                room_id=least_used_room_id,
                                start_time=proposed_start.strftime('%Y-%m-%d %H:%M'),
                                end_time=proposed_end.strftime('%Y-%m-%d %H:%M')
                            )
                            new_room_assignments.append(new_assignment)
                            break  # Found a suitable room and time, move to the next surgery
        
        # Update class attributes or database with new assignments
        self.room_assignments = new_room_assignments

    def is_change_possible(self, surgery, new_room_id):
        """
        Check if changing the room for the surgery to `new_room_id` is possible,
        considering room, surgeon, and equipment availability.
        
        Args:
            surgery (Surgery): The surgery object to check.
            new_room_id (str): The ID of the new room to consider for the surgery.
        
        Returns:
            bool: True if the change is possible, False otherwise.
        """
        # Convert surgery start and end times to the required format, if necessary
        proposed_start = surgery.start_time  # Ensure this matches the format expected by your utility functions
        proposed_end = surgery.end_time      # Ensure this matches the format expected by your utility functions

        # Check if the new room is available at the time of the surgery
        if not is_room_available(self.surgery_room_assignments, new_room_id, proposed_start, proposed_end):
            return False

        # Find the surgeon assigned to this surgery
        surgeon = next((s for s in self.surgeons if s.staff_id == surgery.surgeon_id), None)
        if surgeon is None or not is_surgeon_available(surgeon, proposed_start, proposed_end):
            return False

        # Assuming surgery has a method or attribute to get the required equipment
        # and equipment_inventory is structured as expected by is_equipment_available
        equipment_inventory = {eq.equipment_id: eq for eq in self.surgery_equipments}  # Adapt as necessary
        if not is_equipment_available(surgery, proposed_start, proposed_end, equipment_inventory):
            return False

        # If all checks pass, the change is possible
        return True
    
    def assign_surgery_to_room(self, surgery_id, new_room_id, new_start_time, new_end_time):
        """
        Assigns a surgery to a new room and updates the schedule accordingly.
        
        Args:
        - surgery_id (str): The ID of the surgery to be reassigned.
        - new_room_id (str): The ID of the new room to assign the surgery to.
        - new_start_time (str): The new start time for the surgery in '%Y-%m-%d %H:%M' format.
        - new_end_time (str): The new end time for the surgery in '%Y-%m-%d %H:%M' format.
        """
        # First, check if the new room and time slot are available for the surgery
        if not is_room_available(self.surgery_room_assignments, new_room_id, new_start_time, new_end_time):
            print(f"Room {new_room_id} is not available at the requested time.")
            return False
        
        # Find the existing room assignment for the surgery
        existing_assignment = next((assignment for assignment in self.surgery_room_assignments if assignment.surgery_id == surgery_id), None)
        
        if existing_assignment:
            # Update the room assignment with the new room and times
            existing_assignment.room_id = new_room_id
            existing_assignment.start_time = new_start_time
            existing_assignment.end_time = new_end_time
        else:
            # If no existing assignment found, create a new one
            new_assignment = SurgeryRoomAssignment(
                assignment_id=f"RA{len(self.surgery_room_assignments) + 1}",
                surgery_id=surgery_id,
                room_id=new_room_id,
                start_time=new_start_time,
                end_time=new_end_time
            )
            self.surgery_room_assignments.append(new_assignment)
        
        return True

    def shift_surgery_time(self, surgery_id, shift_minutes):
        """
        Shifts the start and end time of a surgery by a specified number of minutes.
        
        Args:
        - surgery_id (str): The ID of the surgery to shift.
        - shift_minutes (int): The number of minutes to shift the surgery time by. Can be negative or positive.
        
        Returns:
        - bool: True if the surgery time was successfully shifted, False otherwise.
        """
        # Find the room assignment for the specified surgery
        for assignment in self.surgery_room_assignments:
            if assignment.surgery_id == surgery_id:
                # Convert start and end times to datetime objects
                start_time_dt = datetime.strptime(assignment.start_time, '%Y-%m-%d %H:%M')
                end_time_dt = datetime.strptime(assignment.end_time, '%Y-%m-%d %H:%M')
                
                # Calculate new start and end times
                new_start_time_dt = start_time_dt + timedelta(minutes=shift_minutes)
                new_end_time_dt = end_time_dt + timedelta(minutes=shift_minutes)
                
                # Format new times back to strings
                new_start_time = new_start_time_dt.strftime('%Y-%m-%d %H:%M')
                new_end_time = new_end_time_dt.strftime('%Y-%m-%d %H:%M')
                
                # Check if the room is still available at the new times
                if is_room_available(self.surgery_room_assignments, assignment.room_id, new_start_time, new_end_time):
                    # Update the assignment with the new times
                    assignment.start_time = new_start_time
                    assignment.end_time = new_end_time
                    
                    # Additional checks, such as surgeon availability, could be included here
                    
                    return True  # Time shift was successful
                else:
                    print(f"Cannot shift surgery {surgery_id} to the new time slot as it conflicts with existing assignments.")
                    return False  # Room not available at the new time
        
        print(f"No existing assignment found for surgery {surgery_id}.")
        return False  # Surgery ID not found in room assignments

    def can_swap_surgeons(self, surgery_id_1, surgery_id_2):
        """
        Determines if two surgeries can swap their assigned surgeons without violating constraints.
        
        Args:
        - surgery_id_1 (str): The ID of the first surgery.
        - surgery_id_2 (str): The ID of the second surgery.
        
        Returns:
        - bool: True if the surgeons can be swapped, False otherwise.
        """
        # Retrieve the surgeries by their IDs
        surgery_1 = next((s for s in self.surgeries if s.surgery_id == surgery_id_1), None)
        surgery_2 = next((s for s in self.surgeries if s.surgery_id == surgery_id_2), None)
        
        if not surgery_1 or not surgery_2:
            logger.error(f"One or both surgeries not found. Surgery 1 ID: {surgery_id_1}, Surgery 2 ID: {surgery_id_2}")
            return False
        
        surgeon_1 = next((s for s in self.surgeons if s.staff_id == surgery_1.surgeon_id), None)
        surgeon_2 = next((s for s in self.surgeons if s.staff_id == surgery_2.surgeon_id), None)
        
        if not surgeon_1 or not surgeon_2:
            logger.error("One or both assigned surgeons not found for the surgeries.")
            return False
        
        if not surgeon_1.has_expertise_for(surgery_2.surgery_type):
            logger.error(f"Surgeon {surgeon_1.staff_id} lacks expertise for surgery {surgery_2.surgery_id}")
            return False
        
        if not surgeon_2.has_expertise_for(surgery_1.surgery_type):
            logger.error(f"Surgeon {surgeon_2.staff_id} lacks expertise for surgery {surgery_1.surgery_id}")
            return False
        
        if not surgeon_1.is_available(surgery_2.scheduled_time) or not surgeon_2.is_available(surgery_1.scheduled_time):
            logger.error("One or both surgeons are not available for the scheduled time of the other's surgery.")
            return False
        
        # Assuming other checks (like patient consent, equipment availability, etc.) are also required
        # logger.info or logger.warning can be used based on the situation
        
        return True

    def validate_surgeon_swap(self, surgery_id_1, surgery_id_2):
        # Retrieve surgeries by their IDs
        surgery_1 = next((s for s in self.surgeries if s.surgery_id == surgery_id_1), None)
        surgery_2 = next((s for s in self.surgeries if s.surgery_id == surgery_id_2), None)
        
        if not surgery_1 or not surgery_2:
            logger.error("Validation failed: One or both surgeries not found.")
            return False
        
        # Retrieve surgeons assigned to the surgeries
        surgeon_1 = next((s for s in self.surgeons if s.staff_id == surgery_1.surgeon_id), None)
        surgeon_2 = next((s for s in self.surgeons if s.staff_id == surgery_2.surgeon_id), None)
        
        if not surgeon_1 or not surgeon_2:
            logger.error("Validation failed: One or both surgeons not found.")
            return False
        
        # Check if surgeons have the required expertise for the other's surgery
        if not surgeon_1.has_expertise_for(surgery_2.surgery_type):
            logger.error(f"Validation failed: Surgeon {surgeon_1.staff_id} lacks expertise for surgery {surgery_2.surgery_id}.")
            return False

        if not surgeon_2.has_expertise_for(surgery_1.surgery_type):
            logger.error(f"Validation failed: Surgeon {surgeon_2.staff_id} lacks expertise for surgery {surgery_1.surgery_id}.")
            return False
        
        # Check if surgeons are available at the scheduled times of the other's surgery
        # This assumes you have a method to convert surgery scheduled times into datetime objects if they're not already
        if not surgeon_1.is_available(datetime.strptime(surgery_2.scheduled_time, '%Y-%m-%d %H:%M')) or \
        not surgeon_2.is_available(datetime.strptime(surgery_1.scheduled_time, '%Y-%m-%d %H:%M')):
            logger.error("Validation failed: One or both surgeons are not available for the scheduled time of the other's surgery.")
            return False
        
        # Add any additional checks here as needed
        # For example, ensuring that no conflicts arise with surgery room bookings, etc.

        logger.info(f"Validation passed: Surgeons {surgeon_1.staff_id} and {surgeon_2.staff_id} can be swapped for surgeries {surgery_id_1} and {surgery_id_2}.")
        return True

    def update_related_schedules(self, surgery_id_1, surgery_id_2):
        """
        Updates related schedules and notifications after surgeons have been swapped.
        
        Args:
        - surgery_id_1 (str): The ID of the first surgery involved in the swap.
        - surgery_id_2 (str): The ID of the second surgery involved in the swap.
        """
        # Retrieve the surgery and surgeon details
        surgery_1 = next((s for s in self.surgeries if s.surgery_id == surgery_id_1), None)
        surgery_2 = next((s for s in self.surgeries if s.surgery_id == surgery_id_2), None)
        surgeon_1 = next((s for s in self.surgeons if s.staff_id == surgery_1.surgeon_id), None)
        surgeon_2 = next((s for s in self.surgeons if s.staff_id == surgery_2.surgeon_id), None)

        # Example: Update calendars for the involved surgeons
        self.update_surgeon_calendar(surgeon_1, surgery_1, surgery_2)
        self.update_surgeon_calendar(surgeon_2, surgery_2, surgery_1)

        # Notify involved parties of the change
        self.notify_surgeon_of_swap(surgeon_1, surgery_1, surgery_2)
        self.notify_surgeon_of_swap(surgeon_2, surgery_2, surgery_1)
        self.notify_staff_and_patients(surgery_1, surgery_2)

        # Adjust equipment reservations if necessary
        self.adjust_equipment_reservations(surgery_1, surgery_2)

        logger.info(f"Related schedules updated for swapped surgeries {surgery_id_1} and {surgery_id_2}.")



    # Additional methods as needed ...

# Entry point to run the optimization if this script is run directly
if __name__ == "__main__":
    # Initialize data using the functions from initialize_data.py
    surgeries = initialize_surgeries()
    operating_rooms = initialize_operating_rooms()
    surgeons = initialize_surgeons()
    patients = initialize_patients()
    staff_members = initialize_staff_members()
    surgery_equipments = initialize_surgery_equipments()
    surgery_equipment_usages = initialize_surgery_equipment_usages()
    surgery_room_assignments = initialize_surgery_room_assignments()
    surgery_staff_assignments = initialize_surgery_staff_assignments()

    # Equipment inventory for check_equipment_availability (example structure)
    equipment_inventory = {eq.equipment_id: eq.availability for eq in surgery_equipments}

    # Instantiate the scheduler with the initialized data
    scheduler = TabuSearchScheduler(surgeries, surgery_room_assignments, surgeons)

    # Example: Calculate room utilization and equipment availability scores (for demonstration)
    room_utilization_score = scheduler.calculate_room_utilization(surgery_room_assignments, operating_rooms)
    equipment_availability_score = scheduler.check_equipment_availability(surgeries, equipment_inventory)

    print(f"Room Utilization Score: {room_utilization_score}")
    print(f"Equipment Availability Score: {equipment_availability_score}")

    scheduler.run()
