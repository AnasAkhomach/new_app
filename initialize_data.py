from faker import Faker
import random
import sys
import os

# Add the parent directory to sys.path to find MongoDBClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongodb_transaction_manager import MongoDBClient

fake = Faker()
db = MongoDBClient.get_db()



def initialize_patients():
    patients = []
    for _ in range(100):  # Generate 100 patients
        patient = {
            "patient_id": fake.unique.uuid4(),
            "name": fake.name(),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
            "contact_info": {
                "phone": fake.phone_number(),
                "email": fake.email()
            },
            "medical_history": [
                {
                    "condition": fake.word(),
                    "date_diagnosed": fake.date_between(start_date="-10y", end_date="today").strftime('%Y-%m-%d')
                } for _ in range(fake.random_int(min=1, max=5))  # Generate 1-5 medical history records
            ],
            "privacy_consent": fake.boolean()
        }
        patients.append(patient)
    return patients


def initialize_surgeons():
    surgeons = []
    specializations = ["Cardiothoracic Surgery", "Orthopedic Surgery", "Neurology"]
    for _ in range(10):
        surgeons.append({
            "surgeon_id": fake.unique.uuid4(),
            "name": fake.name(),
            "contact_info": {
                "email": fake.email(),
                "phone": fake.phone_number(),
            },
            "specialization": random.choice(specializations),
            "credentials": [fake.sentence() for _ in range(2)],  # Generate 2 credentials
            "availability": [{
                "day": fake.day_of_week(),
                "start": fake.time(),
                "end": fake.time(),
            } for _ in range(random.randint(1, 3))],  # Generate 1-3 availability slots
            "surgeon_preferences": {
                "preferred_operating_room": f"OR{random.randint(1, 10)}"
            }
        })
    return surgeons


def initialize_operating_rooms():
    operating_rooms = []
    for i in range(1, 11):  # Generate 10 operating rooms
        operating_rooms.append({
            "room_id": f"OR{i}",
            "location": f"{fake.city()} - Room {i}",
            "equipment_list": [fake.word() for _ in range(random.randint(1, 5))],  # Generate 1-5 equipment items
        })
    return operating_rooms



def initialize_staff_members():
    staff_members = []
    roles = ["Nurse", "Anesthesiologist", "Technician", "Administrative Staff"]
    for _ in range(10):
        staff_members.append({
            "staff_id": fake.unique.uuid4(),
            "name": fake.name(),
            "role": random.choice(roles),
            "contact_info": {
                "phone": fake.phone_number(),
                "email": fake.email()
            },
            "availability_schedule": [{
                "day": fake.day_of_week(),
                "start": fake.time(),
                "end": fake.time(),
            } for _ in range(random.randint(1, 5))],  # Generate 1-5 availability slots
        })
    return staff_members


def initialize_surgeries():
    surgeries = []
    patient_ids = fetch_ids(collection_name="patients", id_field="patient_id")
    surgeon_ids = fetch_ids(collection_name="surgeons", id_field="surgeon_id")
    room_ids = fetch_ids(collection_name="operating_rooms", id_field="room_id")

    surgery_types = ["Appendectomy", "Gallbladder Removal", "Hip Replacement"]
    for _ in range(10):
        surgeries.append({
            "surgery_id": fake.unique.uuid4(),
            "patient_id": patient_ids,
            "surgeon_id": surgeon_ids,
            "room_id": room_ids,
            "scheduled_date": fake.date_between(start_date="-1y", end_date="today").isoformat(),
            "surgery_type": random.choice(surgery_types),
            "urgency_level": random.choice(["High", "Medium", "Low"]),
            "duration": random.randint(1, 8),  # Duration in hours
            "status": random.choice(["Scheduled", "Completed", "Cancelled"]),
        })
    return surgeries


def fetch_ids(collection_name, id_field):
    # Assume db is a global MongoDB client instance accessible here
    collection = db[collection_name]
    documents = collection.find({}, {id_field: 1})
    ids = [doc[id_field] for doc in documents]
    return ids


def initialize_surgery_equipments():
    surgery_equipments = []
    equipment_types = ["Scalpel", "Forceps", "Surgical Scissors", "Suture"]
    for _ in range(10):
        surgery_equipments.append({
            "equipment_id": fake.unique.uuid4(),
            "name": random.choice(equipment_types),
            "type": random.choice(["Disposable", "Reusable"]),
            "availability": fake.boolean(),
        })
    return surgery_equipments



def initialize_surgery_equipment_usages():
    surgery_equipment_usages = []
    for i in range(1, 11):  # Generate 10 unique equipment usages
        surgery_equipment_usages.append({
            "usage_id": f"SEU00{i}",
            "surgery_id": f"SUR00{i}",
            "equipment_id": f"EQ00{i}"
        })
    return surgery_equipment_usages


def initialize_surgery_staff_assignments(surgery_ids, staff_ids):
    surgery_staff_assignments = []
    roles = ["Lead Surgeon", "Assistant Surgeon", "Nursing Staff", "Technician"]
    for surgery_id in surgery_ids:
        surgery_staff_assignments.append({
            "assignment_id": fake.uuid4(),
            "surgery_id": surgery_id,
            "staff_id": random.choice(staff_ids),
            "role": random.choice(roles),
        })
    return surgery_staff_assignments



from datetime import datetime, timedelta
import random

def initialize_surgery_room_assignments(surgery_ids, room_ids):
    surgery_room_assignments = []
    for surgery_id in surgery_ids:
        start_date = datetime.now() - timedelta(days=random.randint(1, 365))
        end_date = start_date + timedelta(hours=random.randint(1, 8))
        surgery_room_assignments.append({
            "assignment_id": fake.uuid4(),
            "surgery_id": surgery_id,
            "room_id": random.choice(room_ids),
            "start_time": start_date.isoformat(),
            "end_time": end_date.isoformat(),
        })
    return surgery_room_assignments


def initialize_surgery_appointments(surgery_ids, patient_ids, room_ids):
    surgery_appointments = []
    for surgery_id in surgery_ids:
        start_date = datetime.now() - timedelta(days=random.randint(1, 365))
        end_date = start_date + timedelta(hours=random.randint(1, 8))
        surgery_appointments.append({
            "appointment_id": fake.uuid4(),
            "surgery_id": surgery_id,
            "patient_id": random.choice(patient_ids),
            "staff_assignments": [{
                "staff_id": fake.uuid4(),  # Assuming you want to randomly generate or select from staff_ids
                "role": "Lead Surgeon",
            }],
            "room_id": random.choice(room_ids),
            "start_time": start_date.isoformat(),
            "end_time": end_date.isoformat(),
        })
    return surgery_appointments


