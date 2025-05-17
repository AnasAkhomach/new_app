"""Service layer for managing surgery room assignments in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import SurgeryRoomAssignment
import datetime


class SurgeryRoomAssignmentService:
    """Provides services for managing surgery room assignments."""

    @staticmethod
    def create_surgery_room_assignment(db, assignment_data):  # Added db parameter
        """Creates a new surgery room assignment."""
        try:
            # Convert start_time and end_time to datetime if present as string
            for field in ["start_time", "end_time"]:
                if field in assignment_data and isinstance(assignment_data[field], str):
                    assignment_data[field] = datetime.datetime.fromisoformat(
                        assignment_data[field]
                    )
            new_assignment = SurgeryRoomAssignment(
                surgery_id=assignment_data["surgery_id"],
                room_id=assignment_data["room_id"],
                start_time=assignment_data["start_time"],
                end_time=assignment_data["end_time"],
            )
            db.add(new_assignment)
            db.commit()
            db.refresh(new_assignment)
            print(
                f"Surgery room assignment {new_assignment.assignment_id} created successfully."
            )
            return new_assignment.assignment_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating surgery room assignment: {e}")
            return None

    @staticmethod
    def update_surgery_room_assignment(db, assignment_id, update_fields):
        """Updates an existing surgery room assignment record."""
        try:
            result = (
                db.query(SurgeryRoomAssignment)
                .filter_by(assignment_id=assignment_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Room assignment {assignment_id} updated successfully.")
                return True
            print(
                f"No room assignment found with ID {assignment_id} or no new data to update."
            )
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating room assignment: {e}")
            return False

    @staticmethod
    def delete_surgery_room_assignment(db, assignment_id):
        """Deletes a surgery room assignment record."""
        try:
            result = (
                db.query(SurgeryRoomAssignment)
                .filter_by(assignment_id=assignment_id)
                .delete()
            )
            db.commit()
            if result:
                print(f"Room assignment {assignment_id} deleted successfully.")
                return True
            print(f"No room assignment found with ID {assignment_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting room assignment: {e}")
            return False

    @staticmethod
    def get_assignment(db, assignment_id):
        """Retrieves a surgery room assignment by assignment_id and returns a SurgeryRoomAssignment instance."""
        try:
            assignment = (
                db.query(SurgeryRoomAssignment)
                .filter_by(assignment_id=assignment_id)
                .first()
            )
            if assignment:
                return assignment
            print(f"No room assignment found with ID {assignment_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error retrieving room assignment: {e}")
            return None
