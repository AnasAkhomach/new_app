# seed_database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from initialize_data import (
    initialize_patients,
    initialize_staff_members,
    initialize_surgeons,  # Ensure this function is updated for the new Surgeon model
    initialize_operating_rooms,
    initialize_surgeries,
    initialize_surgery_equipments,
    initialize_surgery_equipment_usages,
    initialize_surgery_room_assignments,
    initialize_surgery_staff_assignments,
    initialize_surgery_appointments
)
from mongodb_transaction_manager import MongoDBClient  # Adjusted import

# Get the database object from MongoDBClient
db = MongoDBClient.get_db()

def seed_collection(collection_name, data_initializer, unique_field=None):
    """Helper function to seed a collection with data, using upserts for items with a unique identifier."""
    collection = db[collection_name]
    data = data_initializer()
    for item in data:
        if unique_field:
            # Upsert strategy: Update the document if exists; insert if not
            collection.update_one({unique_field: item[unique_field]}, {'$set': item}, upsert=True)
        else:
            # For collections without a unique field, insert directly
            collection.insert_one(item)
    print(f"Seeding {collection_name} completed.")

if __name__ == "__main__":
    # Seed the collections with initial data
    seed_collection('patients', initialize_patients, 'patient_id')
    seed_collection('staff', initialize_staff_members, 'staff_id')
    seed_collection('surgeons', initialize_surgeons, 'surgeon_id')  # Note the unique_field 'surgeon_id'
    seed_collection('operating_rooms', initialize_operating_rooms, 'room_id')
    seed_collection('surgeries', initialize_surgeries, 'surgery_id')
    seed_collection('equipment', initialize_surgery_equipments, 'equipment_id')
    seed_collection('surgery_equipment_usage', initialize_surgery_equipment_usages)  # No unique field provided
    seed_collection('surgery_room_assignments', initialize_surgery_room_assignments)  # No unique field provided
    seed_collection('surgery_staff_assignments', initialize_surgery_staff_assignments)  # No unique field provided
    seed_collection('surgery_appointments', initialize_surgery_appointments, 'appointment_id')

    print("Database seeding completed.")
