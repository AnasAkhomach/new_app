# operating_room_service.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import OperatingRoom

class OperatingRoomService:
    @staticmethod
    def create_operating_room(operating_room_data):
        """Creates a new operating room record."""
        document = operating_room_data.to_document()
        db.operating_rooms.insert_one(document)
        print(f"Operating Room {document['room_id']} created successfully.")

    @staticmethod
    def update_operating_room(room_id, update_fields):
        """Updates an existing operating room record."""
        db.operating_rooms.update_one({"room_id": room_id}, {"$set": update_fields})
        print(f"Operating Room {room_id} updated successfully.")

    @staticmethod
    def delete_operating_room(room_id):
        """Deletes an operating room record."""
        db.operating_rooms.delete_one({"room_id": room_id})
        print(f"Operating Room {room_id} deleted successfully.")

# Example usage
if __name__ == "__main__":
    new_room = OperatingRoom("OR001", "Main Building - Room 101", ["Scalpel", "Monitor"])
    OperatingRoomService.create_operating_room(new_room)
