from pymongo import MongoClient
import os
from dotenv import load_dotenv
from contextlib import contextmanager


load_dotenv()

# MongoDB connection details from environment variables or default
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "default_db_name") 

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Define collections based on the models
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