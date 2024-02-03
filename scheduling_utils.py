from datetime import datetime, timedelta
from models import Surgeon, OperatingRoom

def shift_time(current_time_str, delta_minutes):
    """
    Shifts the given time string by delta_minutes and returns the new time as a string.
    Args:
    - current_time_str (str): The current time in '%Y-%m-%d %H:%M' format.
    - delta_minutes (int): Minutes to shift the current time, can be negative or positive.
    Returns:
    - str: The new time in '%Y-%m-%d %H:%M' format.
    """
    current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M')
    new_time = current_time + timedelta(minutes=delta_minutes)
    return new_time.strftime('%Y-%m-%d %H:%M')

def find_surgeon(surgeons, surgeon_id):
    """
    Finds a surgeon by their ID from a list of Surgeon objects.
    Args:
    - surgeons (list): List of Surgeon objects.
    - surgeon_id (str): The ID of the surgeon to find.
    Returns:
    - Surgeon: The found Surgeon object or None if not found.
    """
    return next((surgeon for surgeon in surgeons if surgeon.staff_id == surgeon_id), None)

def is_room_available(room_assignments, room_id, start_time_str, end_time_str):
    """
    Checks if the operating room is available during the specified time.
    Args:
    - room_assignments (list): List of SurgeryRoomAssignment objects.
    - room_id (str): The ID of the operating room.
    - start_time_str (str): The start time in '%Y-%m-%d %H:%M' format.
    - end_time_str (str): The end time in '%Y-%m-%d %H:%M' format.
    Returns:
    - bool: True if the room is available, False otherwise.
    """
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')
    for assignment in room_assignments:
        assignment_start = datetime.strptime(assignment.start_time, '%Y-%m-%d %H:%M')
        assignment_end = datetime.strptime(assignment.end_time, '%Y-%m-%d %H:%M')
        if assignment.room_id == room_id and not (end_time <= assignment_start or start_time >= assignment_end):
            return False
    return True

def calculate_room_utilization(room_assignments, operating_rooms):
    """
    Calculate a score based on the utilization rate of operating rooms.
    Args:
    - room_assignments (list): List of SurgeryRoomAssignment objects.
    - operating_rooms (list): List of OperatingRoom objects.
    Returns:
    - float: A score representing the average utilization rate of all operating rooms.
    """
    total_available_time_per_room = 8 * 60  # Assuming 8 hours of operation time per room for simplicity
    total_used_time = 0
    for room in operating_rooms:
        # Sum up the duration of all surgeries assigned to this room
        room_time_used = sum(
            (assignment.end_time - assignment.start_time).total_seconds() / 60
            for assignment in room_assignments if assignment.room_id == room.room_id
        )
        total_used_time += room_time_used

    total_possible_time = total_available_time_per_room * len(operating_rooms)
    utilization_rate = total_used_time / total_possible_time if total_possible_time > 0 else 0

    return utilization_rate * 100  # Convert to percentage

def check_equipment_availability(surgeries, equipment_inventory):
    """
    Check if the required equipment for all surgeries is available.
    Args:
    - surgeries (list): List of Surgery objects, each with a list of required equipment IDs.
    - equipment_inventory (dict): A dictionary with equipment IDs as keys and availability (boolean) as values.
    Returns:
    - int: A score penalizing the lack of available equipment for the scheduled surgeries.
    """
    penalty_per_unavailable_item = -10
    score = 0
    for surgery in surgeries:
        for equipment_id in surgery.required_equipment:
            if not equipment_inventory.get(equipment_id, False):
                score += penalty_per_unavailable_item
    return score

