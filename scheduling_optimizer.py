# This script contains the optimization logic for the surgery scheduling using Tabu Search

from models import OperatingRoom, Patient, Staff, Surgeon, Surgery, SurgeryEquipment, SurgeryEquipmentUsage, SurgeryRoomAssignment, SurgeryStaffAssignment

from initialize_data import (initialize_patients, initialize_staff_members, initialize_surgeons,
                             initialize_operating_rooms, initialize_surgeries, initialize_surgery_equipments,
                             initialize_surgery_equipment_usages, initialize_surgery_room_assignments,
                             initialize_surgery_staff_assignments)

from scheduling_utils import (
    shift_surgery_time, find_surgeon, is_room_available,
    calculate_room_utilization, check_equipment_availability, is_surgeon_available,
    is_equipment_available, get_least_used_room, create_new_neighbor, evaluate_equipment_availability,
    assign_surgery_to_room, shift_surgery_time, can_swap_surgeries, evaluate_room_utilization,
    can_swap_surgeons, find_next_available_time_slot, evaluate_surgeon_preference
)

import random
import copy
from datetime import datetime, timedelta

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from pymongo import MongoClient, errors
from db_config import db
from db_config import mongodb_transaction
from tabu_list import TabuList





class TabuSearchScheduler:

    def __init__(self, db, max_iterations, no_improve_limit):
        self.db = db
        self.max_iterations = max_iterations
        self.no_improve_limit = no_improve_limit
        # Initialize other necessary components here, such as the TabuList
        self.tabu_list = TabuList(max_tenure=10, min_tenure=5)
        # Assume other initial setup has been done, like fetching data

    def find_next_available_time(self, room_id):
        with mongodb_transaction() as session:
            try:
                # Define setup and cleanup times (in minutes)
                setup_time = 15
                cleanup_time = 15

                # Find the latest end time for the given room
                latest_appointment = self.db.surgery_room_assignments.find_one(
                    {"room_id": room_id},
                    sort=[("end_time", -1)],
                    session=session
                )

                if latest_appointment:
                    latest_end_time = datetime.strptime(latest_appointment['end_time'], "%Y-%m-%dT%H:%M:%S")
                    next_available_start = latest_end_time + timedelta(minutes=cleanup_time)
                else:
                    next_available_start = datetime.now() + timedelta(minutes=setup_time)
                
                return next_available_start.isoformat()
            except errors.PyMongoError as e:
                print(f"Database error while finding next available time: {e}")
                return None

    def assign_surgery_to_room_and_time(self, surgery_id, room_id, start_time_str):
        with mongodb_transaction() as session:
            try:
                surgery = self.db.surgeries.find_one({"_id": surgery_id}, session=session)
                if not surgery:
                    print(f"Surgery with ID {surgery_id} not found.")
                    return False
                
                start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
                end_time = start_time + timedelta(minutes=surgery['duration'])

                # Create a surgery room assignment document
                room_assignment = {
                    "surgery_id": surgery_id,
                    "room_id": room_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                }
                
                # Insert the assignment into MongoDB
                self.db.surgery_room_assignments.insert_one(room_assignment, session=session)
                print(f"Surgery {surgery_id} assigned to room {room_id} at {start_time_str} successfully.")
                return True
            except errors.PyMongoError as e:
                print(f"Failed to assign surgery due to database error: {e}")
                return False

    def initialize_solution(self):
        """
        Generates an initial feasible solution by assigning surgeries to available times and rooms.
        Ensures no conflicts with surgeon availability, room availability, and equipment availability.
        """
        with mongodb_transaction(self.db) as session:
            surgeries = list(self.db.surgeries.find({"status": "Scheduled"}, session=session))
            rooms = list(self.db.operating_rooms.find({}, session=session))

            for surgery in surgeries:
                for room in rooms:
                    # Attempt to find the next available time for the surgery in the current room
                    next_available_time = self.find_next_available_time(room["_id"], surgery["duration"], self.db, session)
                    if next_available_time:
                        # Check if the surgeon and required equipment are available at this time
                        surgeon_available = is_surgeon_available(surgery["surgeon_id"], next_available_time["start_time"], next_available_time["end_time"], self.db, session)
                        equipment_available = is_equipment_available(surgery["_id"], next_available_time["start_time"], next_available_time["end_time"], self.db, session)

                        if surgeon_available and equipment_available:
                            # Assign the surgery to this room and time slot
                            self.assign_surgery_to_room_and_time(surgery["_id"], room["_id"], next_available_time["start_time"], self.db, session)
                            break

    def generate_neighbor_solutions(current_schedule, tabu_list, db):
        neighbors = []
        surgeries = list(db.surgeries.find({"status": "Scheduled"}))

        # Sample a subset of surgeries to limit computational expense
        sampled_surgeries = random.sample(surgeries, min(len(surgeries), 5))  # Adjust the sample size as needed

        for surgery in sampled_surgeries:
            surgery_id = surgery["_id"]
            # Attempt to reassign each sampled surgery to a different room or time slot
            for room in db.operating_rooms.find():
                room_id = room["_id"]
                if (surgery_id, room_id) in tabu_list:
                    continue  # Skip if this move is in the Tabu List
                
                # Check if the room is available for the surgery
                new_start_time, new_end_time = find_next_available_time_slot(surgery, room, db)
                if new_start_time and new_end_time:
                    # Clone the current schedule and apply the change
                    neighbor = current_schedule.clone()
                    neighbor.reassign_surgery(surgery_id, room_id, new_start_time, new_end_time)
                    if neighbor.is_feasible(db):
                        neighbors.append(neighbor)

        # Generate swap moves between surgeries
        for i in range(len(sampled_surgeries)):
            for j in range(i + 1, len(sampled_surgeries)):
                surgery1 = sampled_surgeries[i]
                surgery2 = sampled_surgeries[j]
                if (surgery1["_id"], surgery2["_id"]) in tabu_list or (surgery2["_id"], surgery1["_id"]) in tabu_list:
                    continue  # Skip if this swap is in the Tabu List

                # Check if swapping is feasible
                if can_swap_surgeries(surgery1, surgery2, db):
                    # Clone the current schedule and apply the swap
                    neighbor = current_schedule.clone()
                    neighbor.swap_surgeries(surgery1["_id"], surgery2["_id"])
                    if neighbor.is_feasible(db):
                        neighbors.append(neighbor)

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

    def evaluate_solution(solution, db):
        """
        Evaluates the quality of a proposed surgery scheduling solution.
        
        Args:
            solution (dict): The proposed scheduling solution to evaluate.
            db (MongoClient): The database connection for accessing relevant data.
        
        Returns:
            int: The overall score of the solution, with higher scores indicating better solutions.
        """
        # Initialize the overall score
        overall_score = 0
        
        # Evaluate surgeon preferences
        surgeon_preference_score = evaluate_surgeon_preference(solution, db)
        overall_score += surgeon_preference_score
        
        # Evaluate room utilization
        room_utilization_score = evaluate_room_utilization(solution, db)
        overall_score += room_utilization_score
        
        # Evaluate equipment availability
        equipment_availability_score = evaluate_equipment_availability(solution, db)
        overall_score += equipment_availability_score
        
        # You might add additional evaluations here (e.g., patient wait times, staff workloads)
        
        return overall_score
    
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



    def run(self):
        # Initialize the first solution
        current_solution = self.initialize_solution()
        best_solution = current_solution
        best_score = self.evaluate_solution(current_solution)
        
        iterations_since_improvement = 0

        for iteration in range(self.max_iterations):
            if iterations_since_improvement >= self.no_improve_limit:
                print("No improvement in the last {} iterations. Stopping...".format(self.no_improve_limit))
                break
            
            neighbor_solutions = self.generate_neighbor_solutions(current_solution)
            best_neighbor_score = float('-inf')
            best_neighbor = None
            
            for neighbor in neighbor_solutions:
                if self.is_solution_tabu(neighbor) and not self.is_solution_better(neighbor, best_solution):
                    continue  # Skip tabu solutions unless they're better than the best solution found so far
                
                score = self.evaluate_solution(neighbor)
                if score > best_neighbor_score:
                    best_neighbor = neighbor
                    best_neighbor_score = score
            
            if best_neighbor_score > best_score:
                best_solution = best_neighbor
                best_score = best_neighbor_score
                iterations_since_improvement = 0
                print("Iteration {}: New best score found: {}".format(iteration, best_score))
            else:
                iterations_since_improvement += 1
            
            # Update the tabu list for the next iteration
            self.update_tabu_list(current_solution, best_neighbor)
            
            current_solution = best_neighbor  # Move to the next solution
            
        return best_solution  # Return the best solution found

    def initialize_solution(self):
        # Implementation details here
        pass

    def generate_neighbor_solutions(self, current_solution):
        # Implementation details here
        pass

    def evaluate_solution(self, solution):
        # Implementation details here
        pass

    def is_solution_tabu(self, solution):
        # Check if the solution or parts of it are in the tabu list
        pass

    def is_solution_better(self, solution, best_solution):
        # Compare two solutions to determine if one is better
        pass

    def update_tabu_list(self, current_solution, new_solution):
        # Update the tabu list based on the move made
        pass

