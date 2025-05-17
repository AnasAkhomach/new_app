# staff_assignment_service.py
import sys
import os
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Removed: from db_config import db
# Removed: from bson.objectid import ObjectId
from models import (
    StaffAssignment,
)  # Assuming StaffAssignment model exists/will be created for SQLAlchemy


class StaffAssignmentService:
    @staticmethod
    def create_staff_assignment(
        db, assignment_data
    ):  # Added db parameter, changed method signature
        """Creates a new staff assignment."""
        try:
            # Removed MongoDB specific logic
            new_assignment = StaffAssignment(**assignment_data)
            db.add(new_assignment)
            db.commit()
            db.refresh(new_assignment)
            print(
                f"Staff assignment {new_assignment.assignment_id} created successfully."
            )
            return new_assignment.assignment_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating staff assignment: {e}")
            return None

    @staticmethod
    def get_staff_assignment(db, assignment_id):  # Added db parameter
        """Fetches a staff assignment by its ID."""
        try:
            # Removed MongoDB specific logic
            assignment = (
                db.query(StaffAssignment).filter_by(assignment_id=assignment_id).first()
            )
            if assignment:
                return assignment
            else:
                print(f"Staff assignment {assignment_id} not found.")
                return None
        except SQLAlchemyError as e:
            print(f"Error fetching staff assignment: {e}")
            return None

    @staticmethod
    def update_staff_assignment(
        db, assignment_id, update_fields
    ):  # Added db parameter, changed method signature
        """Updates an existing staff assignment."""
        try:
            # Removed MongoDB specific logic
            result = (
                db.query(StaffAssignment)
                .filter_by(assignment_id=assignment_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Staff assignment {assignment_id} updated successfully.")
                return True
            else:
                print(
                    f"Staff assignment {assignment_id} not found or no new data to update."
                )
                return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating staff assignment: {e}")
            return False

    @staticmethod
    def delete_staff_assignment(
        db, assignment_id
    ):  # Added db parameter, changed method signature
        """Deletes a staff assignment."""
        try:
            # Removed MongoDB specific logic
            result = (
                db.query(StaffAssignment)
                .filter_by(assignment_id=assignment_id)
                .delete()
            )
            db.commit()
            if result:
                print(f"Staff assignment {assignment_id} deleted successfully.")
                return True
            else:
                print(f"Staff assignment {assignment_id} not found.")
                return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting staff assignment: {e}")
            return False
