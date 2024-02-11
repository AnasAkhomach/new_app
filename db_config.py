from pymongo import MongoClient
import os
from contextlib import contextmanager
from mongodb_transaction_manager import MongoDBClient  # Make sure to import your MongoDBClient class

# Define collections based on the models
db = MongoDBClient.get_db()  # Use the singleton to access the database
equipment_collection = db.equipment
operating_rooms_collection = db.operating_rooms
patients_collection = db.patients
staff_collection = db.staff
surgeons_collection = db.surgeons
surgeries_collection = db.surgeries
surgery_appointments_collection = db.surgery_appointments
surgery_equipment_usage_collection = db.surgery_equipment_usage
surgery_room_assignments_collection = db.surgery_room_assignments
surgery_staff_assignments_collection = db.surgery_staff_assignments

@contextmanager
def mongodb_transaction():
    client = MongoDBClient.get_client()  # Use the singleton to get the MongoClient instance
    session = client.start_session()
    session.start_transaction()
    try:
        yield session
        session.commit_transaction()
    except Exception as e:
        session.abort_transaction()
        raise e
    finally:
        session.end_session()

    @classmethod
    def get_db(cls):
        if cls._db is None:
            # Adjust these values as necessary
            MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "your_database_name")
            cls._client = MongoClient(MONGO_URI)
            cls._db = cls._client[DATABASE_NAME]
        return cls._db