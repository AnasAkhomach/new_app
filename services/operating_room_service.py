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

from pymongo.errors import PyMongoError, DuplicateKeyError
from db_config import db  # Ensure you have a way to access your db instance

def create_or_update_room(room_data):
    try:
        # Attempt to insert or update room data, handling duplicate room_id
        result = db.operating_rooms.update_one(
            {"room_id": room_data["room_id"]},
            {"$set": room_data},
            upsert=True
        )
        
        if result.upserted_id or result.modified_count > 0:
            print(f"Room {room_data['room_id']} processed successfully.")
            return True
        else:
            print(f"No changes made for Room {room_data['room_id']}.")
            return False
    except DuplicateKeyError:
        print(f"Error: Room ID {room_data['room_id']} already exists. Duplicate entries are not allowed.")
        return False
    except PyMongoError as e:
        print(f"Database operation failed due to error: {e}")
        return False


# Example usage
if __name__ == "__main__":
    try:
        new_room = OperatingRoom("OR001", "Main Building - Room 101", ["ECG Machine", "Anesthesia Machine"])
        OperatingRoomService.create_operating_room(new_room)
    except Exception as e:
        print(f"An error occurred: {e}")