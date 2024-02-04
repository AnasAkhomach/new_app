# seed_database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from initialize_data import (
    initialize_patients,
    initialize_staff_members,
    initialize_surgeons,
    initialize_operating_rooms,
    initialize_surgeries,
    initialize_surgery_equipments,
    initialize_surgery_equipment_usages,
    initialize_surgery_room_assignments,
    initialize_surgery_staff_assignments,
    initialize_surgery_appointments
)
from db_config import surgery_appointments_collection


# Load environment variables
load_dotenv()

# MongoDB connection details from environment variables or default
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "surgery_scheduler_DB")

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

def seed_surgery_appointments():
    appointments_data = initialize_surgery_appointments()
    surgery_appointments_collection.insert_many(appointments_data)



def seed_collection(collection, data_initializer):
    """Helper function to seed a collection with data."""
    data = data_initializer()
    if data:
        collection.insert_many(data)
    else:
        print(f"No data to insert for collection {collection.name}")



if __name__ == "__main__":
    # Seed the collections with initial data
    seed_collection(patients_collection, initialize_patients)
    seed_collection(staff_collection, initialize_staff_members)
    seed_collection(surgeons_collection, initialize_surgeons)
    seed_collection(operating_rooms_collection, initialize_operating_rooms)
    seed_collection(surgeries_collection, initialize_surgeries)
    seed_collection(equipment_collection, initialize_surgery_equipments)
    seed_collection(surgery_equipment_usage_collection, initialize_surgery_equipment_usages)
    seed_collection(surgery_room_assignments_collection, initialize_surgery_room_assignments)
    seed_collection(surgery_staff_assignments_collection, initialize_surgery_staff_assignments)
    seed_surgery_appointments()  # Add this line to seed surgery appointments

    print("Database seeding completed.")
    print("Database seeding completed, including surgery appointments.")

