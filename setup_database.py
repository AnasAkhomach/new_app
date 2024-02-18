from mongodb_transaction_manager import MongoDBClient
from pymongo.errors import OperationFailure
import logging
from manage_duplicates import find_and_handle_all_duplicates
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_indexes(db):
    db = MongoDBClient.get_db()  # Access the database using the MongoDBClient
    
    try:
        # Example: Ensure a unique index for Operating Rooms by Room ID, created in the background
        db.operating_rooms.create_index([("room_id", 1)], unique=True, background=True)
        logger.info("Unique index on room_id in operating_rooms ensured.")

        # Composite index for Surgery Appointments by Start and End Times, created in the background
        db.surgery_appointments.create_index([("start_time", 1), ("end_time", 1)], background=True)
        logger.info("Composite index on start_time and end_time in surgery_appointments ensured.")

        # Index for Staff Assignments in the Staff Collection, created in the background
        db.staff.create_index([("staff_assignments.staff_id", 1)], background=True)
        logger.info("Index on staff_assignments.staff_id in staff collection ensured.")

        # Unique index for Equipment by Equipment ID, created in the background
        db.surgery_equipment.create_index([("equipment_id", 1)], unique=True, background=True)
        logger.info("Unique index on equipment_id in surgery_equipment ensured.")

        # Unique index for Patients by Patient ID, created in the background
        db.patients.create_index([("patient_id", 1)], unique=True, background=True)
        logger.info("Unique index on patient_id in patients collection ensured.")

        # Reviewing and adjusting indexes based on application needs
        logger.info("Review existing indexes for optimization opportunities...")
        
        db.tabu_entries.create_index([
            ("surgeon_id", 1),
            ("room_id", 1),
            ("equipment_id", 1),
            ("time_slot", 1)
        ], background=True)
        logger.info("Composite index on surgeon_id, room_id, equipment_id, and time_slot in tabu_entries ensured.")

    # ... your existing index creation logic ...
        find_and_handle_all_duplicates(db)
        # Now that duplicates are handled, create the unique index
        db.operating_rooms.create_index([("room_id", 1)], unique=True)

        # Example: Drop an index if it's no longer needed, with logging
        # db.collection.drop_index("index_name")
        # logger.info("Dropped unused index: index_name")
        
    except OperationFailure as e:
        logger.error(f"Error creating index: {e}")

def main():
    logger.info("Starting database index management...")
    db = MongoDBClient.get_db()  # Get the database object from your MongoDB client
    create_indexes(db)  # Pass the database object to the create_indexes function
    logger.info("Index management completed. Review and manage indexes regularly as your application evolves.")

if __name__ == "__main__":
    main()
