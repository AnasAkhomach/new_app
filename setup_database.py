from db_config import db
from pymongo.errors import OperationFailure

def create_indexes():
    try:
        # Index for operating room availability checks
        db.surgery_appointments.create_index([("room_id", 1)])
        print("Index on room_id created successfully.")

        # Composite index for efficiently querying appointments by start and end times
        db.surgery_appointments.create_index([("start_time", 1), ("end_time", 1)])
        print("Index on start_time and end_time created successfully.")

        # Index for checking staff assignments and availability
        db.surgery_appointments.create_index([("staff_assignments.staff_id", 1)])
        print("Index on staff_assignments.staff_id created successfully.")

    except OperationFailure as e:
        print(f"Error creating index: {e}")

def main():
    print("Starting database setup...")
    create_indexes()
    print("Database setup completed. Ensure to review and manage indexes as your application evolves.")

if __name__ == "__main__":
    main()
