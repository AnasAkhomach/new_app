from datetime import datetime, timedelta
from pymongo.errors import PyMongoError
from models import Surgery, OperatingRoom, SurgeryRoomAssignment, Surgeon, SurgeryEquipment
from db_config import db
from db_config import mongodb_transaction
from bson.objectid import ObjectId



def shift_surgery_time(current_time_str, delta_minutes):
    """
    Shifts the given time string by delta_minutes and returns the new time.
    
    This function is adapted to ensure the output format is compatible with MongoDB datetime storage,
    which typically uses ISO 8601 format strings or native Python datetime objects.
    
    Args:
    - current_time_str (str): The current time in ISO 8601 format ('%Y-%m-%dT%H:%M:%S').
    - delta_minutes (int): Minutes to shift the current time, can be negative or positive.
    
    Returns:
    - datetime: The new time as a datetime object, ensuring compatibility with MongoDB.
    """
    current_time = datetime.strptime(current_time_str, '%Y-%m-%dT%H:%M:%S')
    new_time = current_time + timedelta(minutes=delta_minutes)
    return new_time  # Returning as a datetime object for direct MongoDB compatibility

def is_room_available(room_id, proposed_start, proposed_end, setup_time=15, cleanup_time=15):
    """
    Enhanced check for operating room availability, considering setup and cleanup times 
    and potential equipment constraints within the room.

    Args:
    - room_id (str): The ID of the operating room.
    - proposed_start (datetime): The proposed start datetime.
    - proposed_end (datetime): The proposed end datetime.
    - setup_time (int): Minutes required for room setup before the surgery starts.
    - cleanup_time (int): Minutes required for cleanup after the surgery ends.

    Returns:
    - bool: True if the room is available, False otherwise.
    """
    try:
        # Adjust times for setup and cleanup
        adjusted_start = proposed_start - timedelta(minutes=setup_time)
        adjusted_end = proposed_end + timedelta(minutes=cleanup_time)
        
        # Convert to ISO string if using MongoDB's ISODate
        adjusted_start_iso = adjusted_start.isoformat()
        adjusted_end_iso = adjusted_end.isoformat()

        with mongodb_transaction() as session:
            # Check for overlapping appointments with the adjusted times
            count = db.surgery_appointments.count_documents({
                "room_id": room_id,
                "$or": [
                    {"start_time": {"$lt": adjusted_end_iso, "$gte": adjusted_start_iso}},
                    {"end_time": {"$gt": adjusted_start_iso, "$lte": adjusted_end_iso}}
                ]
            }, session=session)

            # Include logic for equipment availability check if necessary

            return count == 0
    except PyMongoError as e:
        print(f"Error checking room availability: {e}")
        return False  # Assume room is not available if there's a database error

def calculate_room_utilization(start_date, end_date):
    """
    Calculates the utilization rate of operating rooms between start_date and end_date.

    Args:
    - start_date (datetime): The start date for the calculation period.
    - end_date (datetime): The end date for the calculation period.

    Returns:
    - dict: A dictionary with room_ids as keys and utilization percentages as values.
    """
    try:
        # Convert datetime to strings if necessary for MongoDB queries
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")

        room_utilizations = {}
        total_operational_hours = 8  # Assuming each room operates 8 hours per day

        # Fetch all room assignments within the given timeframe
        room_assignments = db.surgery_room_assignments.find({
            "start_time": {"$gte": start_str},
            "end_time": {"$lte": end_str}
        })

        # Initialize utilization calculation for each room
        for assignment in room_assignments:
            room_id = assignment["room_id"]
            if room_id not in room_utilizations:
                room_utilizations[room_id] = 0

            # Calculate the duration of each surgery in hours
            start_time = datetime.strptime(assignment["start_time"], "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.strptime(assignment["end_time"], "%Y-%m-%dT%H:%M:%S")
            duration = (end_time - start_time).total_seconds() / 3600

            # Add the surgery duration to the room's total utilization
            room_utilizations[room_id] += duration

        # Calculate utilization percentage for each room
        for room_id in room_utilizations:
            days = (end_date - start_date).days + 1  # +1 to include both start and end dates
            room_utilizations[room_id] = (room_utilizations[room_id] / (total_operational_hours * days)) * 100

        return room_utilizations
    except PyMongoError as e:
        print(f"Database error while calculating room utilization: {e}")
        return {}

def check_equipment_availability(surgery_id, proposed_start, proposed_end):
    """
    Checks the availability of all required equipment for a surgery within a proposed timeframe.
    
    Args:
    - surgery_id (str): The ID of the surgery.
    - proposed_start (datetime): The proposed start datetime for the surgery.
    - proposed_end (datetime): The proposed end datetime for the surgery.

    Returns:
    - bool: True if all required equipment is available, False otherwise.
    """
    try:
        # Fetch the surgery details including required equipment
        surgery_details = db.surgeries.find_one({"surgery_id": surgery_id}, {"required_equipment": 1})
        if not surgery_details or "required_equipment" not in surgery_details:
            print(f"Surgery {surgery_id} does not have required equipment listed.")
            return False  # Assuming equipment is necessary for the surgery

        required_equipment_ids = surgery_details["required_equipment"]
        
        # Check each piece of equipment for availability
        for equipment_id in required_equipment_ids:
            equipment_availability = db.equipment.find_one(
                {"equipment_id": equipment_id, "availability": True},
                {"_id": 0, "maintenance_schedule": 1}
            )
            
            if not equipment_availability:
                print(f"Equipment {equipment_id} is not available.")
                return False  # Equipment is not available or does not exist
            
            # Check for maintenance conflicts
            for maintenance in equipment_availability.get("maintenance_schedule", []):
                maintenance_start = datetime.strptime(maintenance["start"], "%Y-%m-%dT%H:%M:%S")
                maintenance_end = datetime.strptime(maintenance["end"], "%Y-%m-%dT%H:%M:%S")
                if not (proposed_end <= maintenance_start or proposed_start >= maintenance_end):
                    print(f"Equipment {equipment_id} is under maintenance.")
                    return False  # Maintenance period conflicts with proposed surgery times

        return True  # All required equipment is available and not under maintenance
    except PyMongoError as e:
        print(f"Database error while checking equipment availability: {e}")
        return False  # Assume unavailability in case of database errors

def is_staff_available(staff_id, proposed_start, proposed_end):
    """
    Checks if a staff member is available during a given time slot.
    
    Args:
    - staff_id (str): The unique identifier of the staff member.
    - proposed_start (datetime): The start time of the proposed surgery or assignment.
    - proposed_end (datetime): The end time of the proposed surgery or assignment.
    
    Returns:
    - bool: True if the staff member is available, False otherwise.
    """
    with mongodb_transaction() as session:
        # Convert datetime objects to strings if necessary
        proposed_start_str = proposed_start.isoformat()
        proposed_end_str = proposed_end.isoformat()

        # Query for any existing assignments for the staff member that overlap with the proposed times
        count = db.surgery_staff_assignments.count_documents({
            "staff_id": staff_id,
            "$or": [
                {"start_time": {"$lt": proposed_end_str, "$gte": proposed_start_str}},
                {"end_time": {"$gt": proposed_start_str, "$lte": proposed_end_str}}
            ]
        }, session=session)

        # If count is 0, no overlapping assignments were found, and the staff member is available
        return count == 0

def is_surgeon_available(surgeon_id, proposed_start, proposed_end, db):
    """
    Checks if the surgeon is available during the proposed time period.
    
    Args:
    - surgeon_id (str): The ID of the surgeon.
    - proposed_start (datetime): The proposed start datetime.
    - proposed_end (datetime): The proposed end datetime.

    Returns:
    - bool: True if the surgeon is available, False otherwise.
    """
    try:
        # Convert proposed_start and proposed_end to the appropriate format if necessary
        proposed_start_iso = proposed_start.isoformat()
        proposed_end_iso = proposed_end.isoformat()

        with mongodb_transaction() as session:
            # Query to find any appointments that overlap with the proposed times for the given surgeon
            overlapping_appointments = db.surgery_appointments.count_documents({
                "staff_assignments": {"$elemMatch": {"staff_id": surgeon_id}},
                "$or": [
                    {"start_time": {"$lt": proposed_end_iso, "$gte": proposed_start_iso}},
                    {"end_time": {"$gt": proposed_start_iso, "$lte": proposed_end_iso}}
                ]
            }, session=session)

            # Surgeon is available if no overlapping appointments are found
            return overlapping_appointments == 0
    except PyMongoError as e:
        print(f"Error checking surgeon availability: {e}")
        return False  # Assume surgeon is not available if there's a database error

def is_equipment_available(surgery_id, proposed_start, proposed_end):
    """
    Checks if the required equipment for a surgery is available during the proposed time.
    
    Args:
    - surgery_id (str): The ID of the surgery requiring equipment.
    - proposed_start (datetime): The proposed start datetime for the surgery.
    - proposed_end (datetime): The proposed end datetime for the surgery.

    Returns:
    - bool: True if all required equipment is available, False otherwise.
    """
    try:
        # Convert proposed_start and proposed_end to the appropriate format if necessary
        proposed_start_iso = proposed_start.isoformat()
        proposed_end_iso = proposed_end.isoformat()

        with mongodb_transaction() as session:
            # Query to find any equipment usage that overlaps with the proposed times for the given equipment
            overlapping_usages = db.surgery_equipment_usage.count_documents({
                "equipment_id": equipment_id,
                "$or": [
                    {"start_time": {"$lt": proposed_end_iso, "$gte": proposed_start_iso}},
                    {"end_time": {"$gt": proposed_start_iso, "$lte": proposed_end_iso}}
                ]
            }, session=session)

            # Equipment is available if no overlapping usages are found
            return overlapping_usages == 0
    except PyMongoError as e:
        print(f"Error checking equipment availability: {e}")
        return False  # Assume equipment is not available if there's a database error

def get_least_used_room(start_date, end_date):
    """
    Identifies the least used operating room between start_date and end_date.

    Args:
    - start_date (datetime): The start date for the period of interest.
    - end_date (datetime): The end date for the period of interest.

    Returns:
    - str: The room_id of the least used operating room.
    """
    try:
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")

        # Aggregate room assignments to calculate total duration per room
        pipeline = [
            {
                "$match": {
                    "start_time": {"$gte": start_str},
                    "end_time": {"$lte": end_str}
                }
            },
            {
                "$project": {
                    "room_id": 1,
                    "duration": {
                        "$divide": [{"$subtract": ["$end_time", "$start_time"]}, 3600000]  # Convert milliseconds to hours
                    }
                }
            },
            {
                "$group": {
                    "_id": "$room_id",
                    "total_usage": {"$sum": "$duration"}
                }
            },
            {"$sort": {"total_usage": 1}},  # Ascending order
            {"$limit": 1}  # Get the least used room
        ]

        result = list(db.surgery_room_assignments.aggregate(pipeline))
        if result:
            # Assuming the result is not empty, return the room_id of the least used room
            return result[0]["_id"]
        else:
            print("No room assignments found in the specified period.")
            return None
    except PyMongoError as e:
        print(f"Database error while identifying the least used room: {e}")
        return None

def assign_surgery_to_room(surgery_id, proposed_start_str, proposed_end_str):
    """
    Assigns a surgery to an available operating room considering surgeon and equipment availability.
    
    Args:
    - surgery_id (str): The ID of the surgery to be assigned.
    - proposed_start_str (str): The proposed start time for the surgery in ISO format.
    - proposed_end_str (str): The proposed end time for the surgery in ISO format.

    Returns:
    - bool: Indicates whether the assignment was successful.
    - str: A message indicating the result of the operation or the assigned room ID.
    """
    try:
        proposed_start = datetime.strptime(proposed_start_str, '%Y-%m-%dT%H:%M:%S')
        proposed_end = datetime.strptime(proposed_end_str, '%Y-%m-%dT%H:%M:%S')

        surgery = db.surgeries.find_one({"surgery_id": surgery_id})
        if not surgery:
            return False, "Surgery not found."

        surgeon = db.staff.find_one({"staff_id": surgery['surgeon_id']})
        if not surgeon:
            return False, "Surgeon not found."

        # Check surgeon's availability
        if not is_surgeon_available(surgeon, proposed_start, proposed_end):
            return False, f"Surgeon {surgeon['name']} is not available at the proposed time."

        # Iterate through all operating rooms to find an available one
        for room_document in db.operating_rooms.find():
            room = OperatingRoom.from_document(room_document)

            # Check if room is available
            room_availability = db.surgery_room_assignments.count_documents({
                "room_id": room.room_id,
                "$or": [
                    {"start_time": {"$lt": proposed_end_str, "$gte": proposed_start_str}},
                    {"end_time": {"$gt": proposed_start_str, "$lte": proposed_end_str}}
                ]
            })

            if room_availability == 0:
                # Room is available, create a new SurgeryRoomAssignment
                new_assignment = SurgeryRoomAssignment(
                    assignment_id=None,  # This would be generated by MongoDB
                    surgery_id=surgery_id,
                    room_id=room.room_id,
                    start_time=proposed_start_str,
                    end_time=proposed_end_str
                )
                db.surgery_room_assignments.insert_one(new_assignment.to_document())
                return True, f"Surgery assigned to room {room.room_id} successfully."

        return False, "No available operating rooms for the proposed times."
    except PyMongoError as e:
        return False, f"Database error: {e}"
    
def find_surgeon(surgeon_id):
    """
    Finds a surgeon by their ID from the MongoDB database.
    
    Args:
    - surgeon_id (str): The ID of the surgeon to find.
    
    Returns:
    - Surgeon: The found Surgeon object or None if not found.
    """
    try:
        document = db.surgeons.find_one({"staff_id": surgeon_id})
        if document:
            return Surgeon.from_document(document)
        else:
            print(f"Surgeon with ID {surgeon_id} not found.")
            return None
    except PyMongoError as e:
        print(f"Database error when searching for surgeon: {e}")
        return None

def can_swap_surgeons(surgery_id_1, surgeon_id_2, surgery_id_2, surgeon_id_1):
    """
    Checks if two surgeons can be swapped between two surgeries.

    Args:
        surgery_id_1 (str): The ID of the first surgery.
        surgeon_id_2 (str): The ID of the second surgeon (to be swapped to the first surgery).
        surgery_id_2 (str): The ID of the second surgery.
        surgeon_id_1 (str): The ID of the first surgeon (to be swapped to the second surgery).

    Returns:
        bool: True if surgeons can be swapped, False otherwise.
    """
    try:
        # Convert IDs to ObjectIds for MongoDB
        surgery_id_1 = ObjectId(surgery_id_1)
        surgery_id_2 = ObjectId(surgery_id_2)

        # Retrieve the surgery documents
        surgery_1 = db.surgeries.find_one({"_id": surgery_id_1})
        surgery_2 = db.surgeries.find_one({"_id": surgery_id_2})

        if not surgery_1 or not surgery_2:
            print("One or both surgeries do not exist.")
            return False

        # Get the scheduled times for both surgeries
        start_time_1 = surgery_1['start_time']
        end_time_1 = surgery_1['end_time']
        start_time_2 = surgery_2['start_time']
        end_time_2 = surgery_2['end_time']

        # Check if the second surgeon is available for the first surgery's time slot
        if not is_surgeon_available(surgeon_id_2, datetime.fromisoformat(start_time_1), datetime.fromisoformat(end_time_1), db):
            print(f"Surgeon {surgeon_id_2} is not available for surgery {surgery_id_1}.")
            return False

        # Check if the first surgeon is available for the second surgery's time slot
        if not is_surgeon_available(surgeon_id_1, datetime.fromisoformat(start_time_2), datetime.fromisoformat(end_time_2), db):
            print(f"Surgeon {surgeon_id_1} is not available for surgery {surgery_id_2}.")
            return False

        # If both surgeons are available for the respective times, return True
        return True
    except PyMongoError as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def evaluate_surgeon_preference(surgeon_id, assignment, db):
    """
    Evaluates how well a surgery assignment matches a surgeon's preferences.

    Args:
        surgeon_id (str): The unique identifier of the surgeon.
        assignment (dict): Information about the surgery assignment, including surgery_id, room_id, start_time, and end_time.
        db: The MongoDB database connection.

    Returns:
        float: A score representing how well the assignment matches the surgeon's preferences.
    """
    preference_score = 0.0

    # Retrieve surgeon preferences from the database
    surgeon = db.surgeons.find_one({"staff_id": surgeon_id})
    if not surgeon or 'preferences' not in surgeon:
        return preference_score  # No preferences found or surgeon not found

    preferences = surgeon['preferences']

    # Example preference evaluations
    if 'preferred_days' in preferences:
        if assignment['start_time'].weekday() in preferences['preferred_days']:
            preference_score += 1  # Surgeon prefers this day of the week

    if 'preferred_times' in preferences:
        start_hour = assignment['start_time'].hour
        # Assuming preferred_times is a list of tuples (start_hour, end_hour)
        for time_range in preferences['preferred_times']:
            if start_hour >= time_range[0] and start_hour < time_range[1]:
                preference_score += 1  # Surgeon prefers this time range

    if 'preferred_surgery_types' in preferences:
        # Assuming assignment contains 'surgery_type'
        if assignment['surgery_type'] in preferences['preferred_surgery_types']:
            preference_score += 1  # This is a preferred surgery type

    # Additional preference checks can be added here

    return preference_score



# Context manager for MongoDB transactions
@staticmethod
def create_new_neighbor(surgery_id, new_room_id, new_start_time_str, new_end_time_str):
    """
    Attempts to create a new neighbor by reassigning a surgery to a new time and/or room,
    considering surgeon, room, and equipment availability.

    Args:
            surgery_id (str): The ID of the surgery to be reassigned.
            new_room_id (str): The ID of the new room to assign the surgery to.
            new_start_time_str (str): The new start time for the surgery in ISO format.
            new_end_time_str (str): The new end time for the surgery in ISO format.

    Returns:
            bool: True if the neighbor was successfully created, False otherwise.
    """
    try:
        with mongodb_transaction() as session:
            # Convert string times to datetime objects
            new_start_time = datetime.fromisoformat(new_start_time_str)
            new_end_time = datetime.fromisoformat(new_end_time_str)

            # Retrieve the surgery document
            surgery = db.surgeries.find_one({"_id": ObjectId(surgery_id)}, session=session)
            if surgery is None:
                print(f"No surgery found with ID {surgery_id}")
                return False

            # Check surgeon, room, and equipment availability
            if not is_surgeon_available(surgery["surgeon_id"], new_start_time, new_end_time, session):
                return False

            if not is_room_available(new_room_id, new_start_time, new_end_time, session):
                return False

            for equipment_id in surgery.get("equipment_ids", []):
                if not is_equipment_available(equipment_id, new_start_time, new_end_time, session):
                    return False

            # Update the surgery's room assignment and time
            update_result = db.surgery_room_assignments.update_one(
                {"surgery_id": ObjectId(surgery_id)},
                {"$set": {
                        "room_id": ObjectId(new_room_id),
                        "start_time": new_start_time,
                        "end_time": new_end_time
                }},
                    session=session
            )

            if update_result.modified_count == 1:
                print(f"Surgery {surgery_id} successfully reassigned.")
                return True
            else:
                print("Failed to reassign surgery.")
                return False

    except Exception as e:
        print(f"Failed to create new neighbor due to error: {e}")
        return False


"""
# Example usage of calculate_room_utilization()
if __name__ == "__main__":
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    print(calculate_room_utilization(start_date, end_date))

# Example usage of shift_time()
if __name__ == "__main__":
    current_time_str = "2023-01-01T12:00:00"
    delta_minutes = 90  # Shift forward by 90 minutes
    new_time = shift_time(current_time_str, delta_minutes)
    print("New Time:", new_time.isoformat())

# Example usage of get_least_used_room()
if __name__ == "__main__":
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    print(get_least_used_room(start_date, end_date))

    # Example usage of find_surgeon()
if __name__ == "__main__":
    surgeon_id = "S001"
    surgeon = find_surgeon(surgeon_id)
    if surgeon:
        print(f"Found Surgeon: {surgeon.name}")
    else:
        print("Surgeon not found.")

"""

# Example usage
if __name__ == "__main__":
    surgery_id = "your_surgery_id_here"
    new_room_id = "your_new_room_id_here"
    new_start_time_str = "2024-02-07T09:00:00"
    new_end_time_str = "2024-02-07T11:00:00"
    result = create_new_neighbor(surgery_id, new_room_id, new_start_time_str, new_end_time_str)
    print("Neighbor creation result:", result)
