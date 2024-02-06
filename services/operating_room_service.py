# operating_room_service.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_config import db
from models import OperatingRoom
from pymongo.errors import PyMongoError


class OperatingRoomService:
    @staticmethod
    def create_operating_room(operating_room_data):
        """Creates a new operating room record."""
        try:
            document = operating_room_data.to_document()
            db.operating_rooms.insert_one(document)
            print(f"Operating room {document['room_id']} created successfully.")
        except PyMongoError as e:
            print(f"Error creating operating room: {e}")

    @staticmethod
    def get_operating_room(room_id):
        """Retrieves an operating room by room_id and returns an OperatingRoom instance."""
        try:
            document = db.operating_rooms.find_one({"room_id": room_id})
            if document:
                return OperatingRoom.from_document(document)
            else:
                print(f"No operating room found with ID {room_id}")
                return None
        except PyMongoError as e:
            print(f"Error retrieving operating room: {e}")
            return None

# Example usage
if __name__ == "__main__":
    try:
        new_room = OperatingRoom("OR001", "Main Building - Room 101", ["ECG Machine", "Anesthesia Machine"])
        OperatingRoomService.create_operating_room(new_room)
    except Exception as e:
        print(f"An error occurred: {e}")